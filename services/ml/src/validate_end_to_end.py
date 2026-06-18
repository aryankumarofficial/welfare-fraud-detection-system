import asyncio
from argparse import ArgumentParser
from datetime import datetime

from sqlalchemy import select

from src.db.models.student_profile import StudentProfile
from src.db.session import get_db_session
from src.services.prediction_service import PredictionService
from src.services.snapshot_generator import SnapshotGenerator


async def run_validation(limit: int | None = None) -> None:
    async with get_db_session() as session:
        result = await session.execute(select(StudentProfile.id).order_by(StudentProfile.external_id))
        profile_ids = [row[0] for row in result.all()]

        if limit is not None:
            profile_ids = profile_ids[:limit]

        print(f"Found {len(profile_ids)} profiles for validation.")

        snapshot_generator = SnapshotGenerator(session)
        prediction_service = PredictionService(session)

        generated_snapshots = 0
        generated_predictions = 0
        failed_snapshots = 0
        failed_predictions = 0

        for index, profile_id in enumerate(profile_ids, start=1):
            try:
                snapshot_result = await snapshot_generator.generate_for_profile(profile_id)
                generated_snapshots += 1
                print(f"[{index}/{len(profile_ids)}] Snapshot generated for profile {profile_id}")
            except Exception as exc:
                failed_snapshots += 1
                print(f"[{index}/{len(profile_ids)}] Snapshot generation failed for {profile_id}: {exc}")
                continue

            try:
                await prediction_service.predict_for_feature_snapshot(
                    student_profile_id=profile_id,
                    feature_snapshot_id=snapshot_result.snapshot.id,
                )
                generated_predictions += 1
                print(f"[{index}/{len(profile_ids)}] Prediction generated for profile {profile_id}")
            except Exception as exc:
                failed_predictions += 1
                print(f"[{index}/{len(profile_ids)}] Prediction failed for {profile_id}: {exc}")

        print("\nValidation complete")
        print(f"Snapshots generated: {generated_snapshots}")
        print(f"Predictions generated: {generated_predictions}")
        print(f"Snapshot failures: {failed_snapshots}")
        print(f"Prediction failures: {failed_predictions}")
        print(f"Validation executed at: {datetime.now().isoformat()}")


def main() -> None:
    parser = ArgumentParser(description="Validate imported records through snapshot and prediction pipelines.")
    parser.add_argument("--limit", type=int, default=20, help="Number of profiles to validate. Use 0 for all.")
    args = parser.parse_args()
    limit = args.limit if args.limit > 0 else None
    asyncio.run(run_validation(limit=limit))


if __name__ == "__main__":
    main()
