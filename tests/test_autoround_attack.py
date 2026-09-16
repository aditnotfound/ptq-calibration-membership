from __future__ import annotations

from itertools import product
from string import ascii_lowercase
import json

import numpy as np
import pytest
import torch
from torch import nn

from calibtrace.autoround_attack import (
    _candidate_crossfit,
    _jsonl_corpus_metadata,
    _reference_utility,
    attach_experiment_contract,
    load_record_pool,
    make_population_design,
    prepare_resumable_scores,
    synthetic_records,
    text_records,
    _reconstruction_scores,
)


class FakeTokenizer:
    """A byte-pair vocabulary shaped like the OPT tokenizer's word-initial tokens."""

    def get_vocab(self) -> dict[str, int]:
        words = [
            "Ġ" + "".join(letters)
            for letters in product(ascii_lowercase[:8], repeat=4)
        ]
        return {word: index for index, word in enumerate(words)}


class FakeTextTokenizer:
    eos_token_id = 999

    def encode(self, value: str, add_special_tokens: bool = False) -> list[int]:
        assert not add_special_tokens
        return [len(token) for token in value.split()]


class TinyCausalModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.proj = nn.Linear(1, 1, bias=False)
        with torch.no_grad():
            self.proj.weight.fill_(1.0)

    def forward(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:
        del attention_mask
        return self.proj(input_ids.float().unsqueeze(-1))


def test_reconstruction_scores_support_float32_residual_arithmetic() -> None:
    model = TinyCausalModel().eval()
    candidates = torch.full((2, 4), 1_000, dtype=torch.long)
    quantized_weights = {"proj": torch.full_like(model.proj.weight, 65_000.0)}

    aggregate, layerwise = _reconstruction_scores(
        model,
        quantized_weights,
        candidates,
        device=torch.device("cpu"),
        chunk=1,
        compute_dtype="float32",
    )

    assert aggregate.shape == (2,)
    assert layerwise.shape == (2, 1)
    assert np.isfinite(aggregate).all()
    assert np.isfinite(layerwise).all()


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is unavailable")
def test_reconstruction_scores_accept_cpu_weights_for_a_cuda_base() -> None:
    model = TinyCausalModel().cuda().eval()
    candidates = torch.arange(8, dtype=torch.long).reshape(2, 4)
    quantized_weights = {"proj": torch.full((1, 1), 0.75, dtype=torch.float32)}

    aggregate, layerwise = _reconstruction_scores(
        model,
        quantized_weights,
        candidates,
        device=torch.device("cuda"),
        chunk=1,
        compute_dtype="float32",
    )

    assert aggregate.shape == (2,)
    assert layerwise.shape == (2, 1)
    assert np.isfinite(aggregate).all()


def test_population_holds_every_margin_fixed() -> None:
    design = make_population_design(
        calibration_size=128,
        targets=16,
        shadow_artifacts=8,
        test_artifacts=4,
        pool_size=512,
        seed=5,
    )
    membership = np.asarray(design["membership"], dtype=bool)
    assert membership.sum(axis=1).tolist() == [8] * 12
    assert membership[:8].sum(axis=0).tolist() == [4] * 16
    assert membership[8:].sum(axis=0).tolist() == [2] * 16
    for record, row in zip(design["artifacts"], membership, strict=True):
        calibration_indices = set(record["calibration_indices"])
        assert len(calibration_indices) == 128
        # Targets occupy the first pool positions; membership must match the design exactly.
        for position in range(16):
            assert (position in calibration_indices) == bool(row[position])
        assert min(calibration_indices - set(range(16)), default=16) >= 16


def test_reference_records_are_held_out_of_every_calibration_set() -> None:
    design = make_population_design(
        calibration_size=128,
        targets=16,
        shadow_artifacts=8,
        test_artifacts=4,
        pool_size=512,
        seed=5,
        reference_records=8,
    )
    references = set(range(16, 24))
    for record in design["artifacts"]:
        assert not references & set(record["calibration_indices"])
    assert design["reference_records"] == 8


def test_synthetic_records_are_unique_and_heterogeneous() -> None:
    records = synthetic_records(
        FakeTokenizer(), count=64, seqlen=64, seed=3, vocabulary_size=1024, topic_size=16
    )
    assert records.shape == (64, 64)
    assert len(np.unique(records.numpy(), axis=0)) == 64
    # Each record draws its own topic vocabulary, so records rarely share their token support.
    supports = [set(row.tolist()) for row in records]
    overlaps = [
        len(supports[first] & supports[second])
        for first in range(8)
        for second in range(first + 1, 8)
    ]
    assert max(overlaps) < min(len(support) for support in supports[:8])


def test_synthetic_records_are_deterministic() -> None:
    first = synthetic_records(FakeTokenizer(), count=8, seqlen=32, seed=9, vocabulary_size=512)
    second = synthetic_records(FakeTokenizer(), count=8, seqlen=32, seed=9, vocabulary_size=512)
    assert first.equal(second)


def test_synthetic_records_support_a_no_nonce_control() -> None:
    records = synthetic_records(
        FakeTokenizer(),
        count=16,
        seqlen=32,
        seed=9,
        vocabulary_size=512,
        topic_size=512,
        concentration=50.0,
        nonce_length=0,
    )
    assert records.shape == (16, 32)
    assert len(np.unique(records.numpy(), axis=0)) == 16


def test_text_records_pack_a_deterministic_jsonl_corpus(tmp_path) -> None:
    path = tmp_path / "corpus.jsonl"
    payloads = [
        {"text": "one two three four five six seven eight nine ten"},
        {"text": "eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen"},
        {"text": "nineteen twenty twentyone twentytwo twentythree twentyfour"},
    ]
    path.write_text(
        "".join(json.dumps(payload) + "\n" for payload in payloads), encoding="utf-8"
    )
    first = text_records(FakeTextTokenizer(), path=path, count=2, seqlen=8, seed=4)
    second = text_records(FakeTextTokenizer(), path=path, count=2, seqlen=8, seed=4)
    assert first.equal(second)
    assert first.shape == (2, 8)


def test_jsonl_corpus_metadata_records_dates_and_identifiers(tmp_path) -> None:
    path = tmp_path / "corpus.jsonl"
    payloads = [
        {
            "id": "paper-b",
            "published": "2024-02-01T00:00:00Z",
            "source": "test archive",
            "query": "category:test",
            "text": "second",
        },
        {
            "id": "paper-a",
            "published": "2024-01-01T00:00:00Z",
            "source": "test archive",
            "query": "category:test",
            "text": "first",
        },
    ]
    path.write_text(
        "".join(json.dumps(payload) + "\n" for payload in payloads), encoding="utf-8"
    )
    metadata = _jsonl_corpus_metadata(path)
    assert metadata["document_count"] == 2
    assert metadata["earliest_published"] == "2024-01-01T00:00:00Z"
    assert metadata["latest_published"] == "2024-02-01T00:00:00Z"
    assert metadata["sources"] == ["test archive"]
    assert len(metadata["identifier_sha256"]) == 64


def test_text_records_and_metadata_apply_the_same_publication_filter(tmp_path) -> None:
    path = tmp_path / "corpus.jsonl"
    payloads = [
        {
            "id": "old",
            "published": "2025-04-30T23:59:59Z",
            "source": "test archive",
            "query": "category:test",
            "text": "old tokens must stay outside the packed stream",
        },
        {
            "id": "new-a",
            "published": "2025-05-01T00:00:01Z",
            "source": "test archive",
            "query": "category:test",
            "text": "one two three four five six seven eight nine ten",
        },
        {
            "id": "new-b",
            "published": "2025-06-01T00:00:00Z",
            "source": "test archive",
            "query": "category:test",
            "text": "eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen",
        },
    ]
    path.write_text(
        "".join(json.dumps(payload) + "\n" for payload in payloads), encoding="utf-8"
    )
    cutoff = "2025-05-01T00:00:00Z"
    records = text_records(
        FakeTextTokenizer(),
        path=path,
        count=1,
        seqlen=8,
        seed=4,
        published_after=cutoff,
    )
    metadata = _jsonl_corpus_metadata(path, published_after=cutoff)
    assert records.shape == (1, 8)
    assert metadata["document_count"] == 2
    assert metadata["earliest_published"] == "2025-05-01T00:00:01Z"
    assert metadata["row_filter_published_after"] == cutoff


def test_record_loader_enforces_publication_cutoff(tmp_path) -> None:
    path = tmp_path / "corpus.jsonl"
    path.write_text(
        json.dumps(
            {
                "id": "paper-a",
                "published": "2023-12-31T12:00:00Z",
                "source": "test archive",
                "query": "category:test",
                "text": "one two three four five six",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="does not postdate"):
        load_record_pool(
            FakeTextTokenizer(),
            cfg={
                "record_source": "text_jsonl",
                "record_text_path": str(path),
                "record_published_after": "2023-12-31T23:59:59Z",
            },
            config_path=tmp_path / "configs" / "test.yaml",
            count=1,
            seqlen=4,
            seed=2,
        )


def test_reference_utility_uses_calibration_excluded_records() -> None:
    quantized = np.asarray([[-2.0, -2.2], [-2.1, -2.3]])
    gap = np.asarray([[-0.1, -0.2], [-0.1, -0.2]])
    utility = _reference_utility(
        {
            "output_logprob__reference": quantized,
            "output_logprob_gap__reference": gap,
        }
    )
    assert utility is not None
    assert utility["reference_decisions"] == 4
    assert utility["quantized_mean_logprob"] == pytest.approx(-2.15)
    assert utility["base_mean_logprob"] == pytest.approx(-2.0)
    assert utility["mean_logprob_change"] == pytest.approx(-0.15)
    assert utility["perplexity_ratio_quantized_over_base"] == pytest.approx(np.exp(0.15))


def test_resume_contract_rejects_stale_scores(tmp_path) -> None:
    design = make_population_design(
        calibration_size=8,
        targets=4,
        shadow_artifacts=4,
        test_artifacts=2,
        pool_size=32,
        seed=5,
    )
    attach_experiment_contract(
        design,
        record_metadata={"source": "test", "pool_sha256": "a" * 64},
        contract={"library": "test", "bits": 4},
    )
    manifest = tmp_path / "manifest.json"
    scores = tmp_path / "scores.jsonl"
    prepare_resumable_scores(scores, manifest, design)
    row = {
        "artifact_id": 0,
        "experiment_sha256": "stale",
        "split": design["artifacts"][0]["split"],
        "member_target_positions": design["artifacts"][0]["member_target_positions"],
        "calibration_indices_sha256": design["artifacts"][0]["calibration_indices_sha256"],
    }
    scores.write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="stale or missing"):
        prepare_resumable_scores(scores, manifest, design)


def test_candidate_crossfit_excludes_evaluated_candidates() -> None:
    rng = np.random.default_rng(12)
    design = make_population_design(
        calibration_size=16,
        targets=8,
        shadow_artifacts=8,
        test_artifacts=4,
        pool_size=64,
        seed=7,
    )
    membership = np.asarray(design["membership"], dtype=bool)
    signal = membership.astype(float) + rng.normal(0.0, 0.05, membership.shape)
    corrected = {
        "artifact_reconstruction": signal,
        "output_logit_mse": rng.normal(size=membership.shape),
        "output_kl": rng.normal(size=membership.shape),
        "output_logprob": rng.normal(size=membership.shape),
        "output_logprob_gap": rng.normal(size=membership.shape),
    }
    layers = np.stack((signal, rng.normal(size=membership.shape)), axis=-1)
    result = _candidate_crossfit(
        corrected=corrected,
        corrected_layers=layers,
        membership=membership,
        shadow_count=8,
        regularization_grid=(1.0, 0.1),
        folds=2,
        seed=3,
        bootstrap_replicates=20,
        bootstrap_seed=4,
    )
    assert result["metrics"]["artifact_reconstruction"]["auroc"] > 0.99
    for fold in result["selections"]:
        assert set(fold["training_candidates"]).isdisjoint(fold["held_out_candidates"])


def test_candidate_crossfit_predictions_ignore_excluded_shadow_scores() -> None:
    rng = np.random.default_rng(21)
    design = make_population_design(
        calibration_size=16,
        targets=8,
        shadow_artifacts=8,
        test_artifacts=4,
        pool_size=64,
        seed=9,
    )
    membership = np.asarray(design["membership"], dtype=bool)
    corrected = {
        "artifact_reconstruction": membership.astype(float) + rng.normal(
            0.0, 0.1, membership.shape
        ),
        "output_logit_mse": rng.normal(size=membership.shape),
        "output_kl": rng.normal(size=membership.shape),
        "output_logprob": rng.normal(size=membership.shape),
        "output_logprob_gap": rng.normal(size=membership.shape),
    }
    layers = np.stack(
        (corrected["artifact_reconstruction"], rng.normal(size=membership.shape)),
        axis=-1,
    )
    arguments = {
        "membership": membership,
        "shadow_count": 8,
        "regularization_grid": (1.0, 0.1),
        "folds": 2,
        "seed": 5,
        "bootstrap_replicates": 20,
        "bootstrap_seed": 6,
    }
    original = _candidate_crossfit(
        corrected={name: value.copy() for name, value in corrected.items()},
        corrected_layers=layers.copy(),
        **arguments,
    )
    excluded = np.asarray(original["selections"][0]["held_out_candidates"], dtype=int)
    perturbed = {name: value.copy() for name, value in corrected.items()}
    for values in perturbed.values():
        values[:8, excluded] += 1_000_000.0
    perturbed_layers = layers.copy()
    perturbed_layers[:8, excluded] += 1_000_000.0
    repeated = _candidate_crossfit(
        corrected=perturbed,
        corrected_layers=perturbed_layers,
        **arguments,
    )
    assert (
        original["selections"][0]["held_out_prediction_sha256"]
        == repeated["selections"][0]["held_out_prediction_sha256"]
    )
