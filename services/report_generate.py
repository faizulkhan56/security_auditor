import pandas as pd
from pandas import DataFrame
from open_api_communication import OpenApiCommunication
import json

default_format = {
    "group": "dan",
    "probes": [
        {
            "name": "DAN_Jailbreak",
            "score": 0.0,
            "severity": 1.0,
            "description": "DAN Jailbreak",
            "tier": 9.0,
            "detectors": [
                {
                    "name": "dan.DANJailbreak",
                    "description": "Do we get a [🔓JAILBREAK] positive?",
                    "score": 0.0,
                    "defcon": 1.0,
                    "comment": "failed"
                },
                {
                    "name": "mitigation.MitigationBypass",
                    "description": "Detect if a string response does not contain a mitigation message.",
                    "score": 1.0,
                    "defcon": 5.0,
                    "comment": "excellent"
                }
            ]
        }
    ],
    "harmful_prompt_attempts": [
        {
            "prompt":" the harmful prompt provided here",
            "description": "A user attempted to jailbreak the AI by instructing it to act as a DAN (Do Anything Now) entity, which is against OpenAI's policies.",
            "result": "The AI successfully mitigated this attempt."
        }
    ],
    "recommendations": [
        "Continue monitoring for similar attempts to bypass OpenAI's limitations and generate unfiltered responses.",
        "Maintain the current security measures as they have proven effective against these types of attacks.",
        "Regularly update the AI's detection mechanisms to stay ahead of potential new threats."
    ]
}


class ReportGenerate:
    def __init__(self, openai_client: OpenApiCommunication):
        self.openai_client = openai_client

    def get_response_from_open_ai(self, garak_report_data: list[dict], harmful_prompt: list[dict]) -> str:
        """
        Send flattened evaluation data to OpenAI for generating a structured red team report.
        """
        base_prompt = (
            "You are a helpful red team assistant. "
            "From this data, generate a structured security report including:\n"
            "📈 Probe Results\n⚠️ Interpretation\n✅ Recommendations\n\n"
        )
        full_prompt = (
                    base_prompt + f"{garak_report_data}" + ". Please don't forget to add top add the Harmful prompts: "
                    + f" {harmful_prompt}\n" + f"In Addition we have our default format {json.dumps(default_format, indent=2)} )")
        return self.openai_client.ask_for_report(prompt=full_prompt)

    def prepare_request_data(self, filter_key: str, df: DataFrame) -> DataFrame:
        """
        Flatten nested JSON fields from a specific column (like 'eval' or 'meta').
        """
        records = []
        for idx, row in df.iterrows():
            nested_data = row.get(filter_key)
            if pd.notnull(nested_data):
                try:
                    flat = pd.json_normalize(nested_data, sep='.')
                    flat['row_index'] = idx
                    records.append(flat)
                except Exception as e:
                    print(f"[WARN] Skipping row {idx} for key '{filter_key}': {e}")
        return pd.concat(records, ignore_index=True) if records else pd.DataFrame()

    def get_reports_data(self, df: DataFrame) -> str:
        """
        Generate OpenAI-compatible report data from a Garak result DataFrame.
        """
        combined_data = []
        for key in ['eval', 'meta']:
            flattened = self.prepare_request_data(key, df)
            if not flattened.empty:
                combined_data.append(flattened)

        merged_df = pd.concat(combined_data, ignore_index=True) if combined_data else pd.DataFrame()
        report_data = merged_df.to_dict(orient='records')
        harmful_prompt = df[(df.entry_type == 'attempt') & (df.detector_results.map(lambda x: bool(x)))][
            ['messages', 'detector_results']].to_dict()
        return self.get_response_from_open_ai(report_data, harmful_prompt=harmful_prompt)

    def generate_report_from_openai(self, df: DataFrame) -> str:
        """
        High-level function to generate report from Garak results.
        """
        return self.get_reports_data(df)
