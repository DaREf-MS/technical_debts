from src.reports.duplication_report import DuplicationReport

class DuplicationToolInterface:
    def run(self, dir : str, file_extensions : set[str]) -> list[DuplicationReport]:
        return []