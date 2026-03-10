from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TaxonomyManager:
    """Gestisce la tassonomia dei 128 formati creativi e i criteri di qualità."""

    def __init__(self) -> None:
        self._taxonomy: dict[str, Any] = {}
        self._quality_criteria: dict[str, Any] = {}
        # Indice piatto: format_id -> {format_data + macro info}
        self._formats_index: dict[str, dict[str, Any]] = {}
        # Indice macro: macro_id (int) -> {macro_data}
        self._macro_index: dict[int, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Caricamento
    # ------------------------------------------------------------------

    def load_taxonomy(self, path: str | Path) -> dict[str, Any]:
        """Carica taxonomy.json e costruisce gli indici interni.

        Raises:
            FileNotFoundError: se il file non esiste.
            ValueError: se la struttura JSON non è quella attesa.
        """
        taxonomy_path = Path(path)
        if not taxonomy_path.exists():
            raise FileNotFoundError(f"File tassonomia non trovato: {taxonomy_path}")

        with taxonomy_path.open(encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)

        if "macro_categories" not in data:
            raise ValueError(
                "Campo 'macro_categories' mancante nel file tassonomia"
            )

        self._taxonomy = data
        self._formats_index = {}
        self._macro_index = {}

        for macro in data["macro_categories"]:
            macro_id: int = macro["id"]
            self._macro_index[macro_id] = macro

            for fmt in macro.get("formats", []):
                enriched = dict(fmt)
                enriched["macro_category_id"] = macro_id
                enriched["macro_category_name"] = macro["name"]
                self._formats_index[fmt["id"]] = enriched

        return data

    def load_quality_criteria(self, path: str | Path) -> dict[str, Any]:
        """Carica quality_criteria.json.

        Raises:
            FileNotFoundError: se il file non esiste.
            ValueError: se la struttura JSON non è quella attesa.
        """
        criteria_path = Path(path)
        if not criteria_path.exists():
            raise FileNotFoundError(
                f"File criteri qualità non trovato: {criteria_path}"
            )

        with criteria_path.open(encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)

        if "format_criteria_map" not in data:
            raise ValueError(
                "Campo 'format_criteria_map' mancante nel file criteri qualità"
            )

        self._quality_criteria = data
        return data

    # ------------------------------------------------------------------
    # Accesso ai dati
    # ------------------------------------------------------------------

    def get_format_by_id(self, format_id: str) -> dict[str, Any]:
        """Restituisce il formato arricchito con info sulla macro-categoria.

        Raises:
            KeyError: se format_id non esiste nella tassonomia caricata.
        """
        if format_id not in self._formats_index:
            raise KeyError(
                f"Formato '{format_id}' non trovato. "
                "Verificare che load_taxonomy() sia stato chiamato."
            )
        return self._formats_index[format_id]

    def get_macro_category(self, macro_id: int) -> dict[str, Any]:
        """Restituisce la macro-categoria completa (con lista formati).

        Raises:
            KeyError: se macro_id non esiste.
        """
        if macro_id not in self._macro_index:
            raise KeyError(
                f"Macro-categoria ID {macro_id} non trovata. "
                "Verificare che load_taxonomy() sia stato chiamato."
            )
        return self._macro_index[macro_id]

    def get_all_format_ids(self) -> list[str]:
        """Restituisce tutti i format_id ordinati numericamente."""
        return sorted(
            self._formats_index.keys(),
            key=lambda fid: [int(p) for p in fid.split(".")],
        )

    def get_criteria_for_format(self, format_id: str) -> list[dict[str, Any]]:
        """Restituisce i criteri di qualità per un formato specifico.

        Il formato è <criterio_id, peso>. Se la tassonomia non ha criteri
        espliciti per il format_id, torna i criteri della macro-categoria
        a cui appartiene il formato (fallback per macro).

        Raises:
            RuntimeError: se load_quality_criteria() non è stato chiamato.
            KeyError: se né il formato né la sua macro-categoria hanno criteri.
        """
        if not self._quality_criteria:
            raise RuntimeError(
                "Criteri qualità non caricati. "
                "Chiamare load_quality_criteria() prima."
            )

        criteria_map: dict[str, Any] = self._quality_criteria.get(
            "format_criteria_map", {}
        )

        if format_id in criteria_map:
            entry = criteria_map[format_id]
            return self._build_criteria_list(entry)

        # Fallback: cerca per macro-categoria
        if format_id in self._formats_index:
            macro_id = self._formats_index[format_id]["macro_category_id"]
            macro_key = str(macro_id)
            if macro_key in criteria_map:
                entry = criteria_map[macro_key]
                return self._build_criteria_list(entry)

        raise KeyError(
            f"Nessun criterio qualità trovato per il formato '{format_id}'"
        )

    # ------------------------------------------------------------------
    # Generazione testo per prompt
    # ------------------------------------------------------------------

    def build_taxonomy_for_prompt(self) -> str:
        """Genera la rappresentazione testuale della tassonomia da iniettare nei prompt.

        Produce un testo compatto con macro-categorie e formati, adatto per
        essere inserito in un system/user prompt LLM.

        Raises:
            RuntimeError: se load_taxonomy() non è stato chiamato.
        """
        if not self._taxonomy:
            raise RuntimeError(
                "Tassonomia non caricata. Chiamare load_taxonomy() prima."
            )

        lines: list[str] = []
        lines.append(
            f"TAXONOMY OF {self._taxonomy.get('total_formats', '?')} "
            "ADVERTISING CREATIVE FORMATS:\n"
        )

        for macro in self._taxonomy.get("macro_categories", []):
            macro_id: int = macro["id"]
            macro_name: str = macro["name"]
            lines.append(f"\n## MACRO-CATEGORY {macro_id}: {macro_name.upper()}")

            for fmt in macro.get("formats", []):
                fmt_id: str = fmt["id"]
                fmt_name: str = fmt["name"]
                description: str = fmt.get("description", "")
                visual_signals: list[str] = fmt.get("visual_signals", [])

                line = f"{fmt_id}  {fmt_name}"
                if description:
                    line += f" - {description}"
                if visual_signals:
                    signals_str = ", ".join(visual_signals[:3])
                    line += f" [{signals_str}]"
                lines.append(line)

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Helpers interni
    # ------------------------------------------------------------------

    @staticmethod
    def _build_criteria_list(entry: dict[str, Any]) -> list[dict[str, Any]]:
        """Normalizza un entry di criteria_map in lista di dict uniformi."""
        criteria_names: list[str] = entry.get("criteria", [])
        weights: dict[str, float] = entry.get("weights", {})

        return [
            {
                "criterion": name,
                "weight": weights.get(name, 1.0),
            }
            for name in criteria_names
        ]
