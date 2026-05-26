"""Test rápido del genome_refresh_scheduler — Sprint 91.9."""

import os
import sys

sys.path.insert(0, ".")

from kernel.genome_refresh_scheduler import (
    shutdown_genome_refresh_scheduler,
    start_genome_refresh_scheduler,
)


def test_disabled():
    os.environ["GENOME_REFRESH_DISABLED"] = "1"
    sched = start_genome_refresh_scheduler()
    assert sched is None, f"Esperaba None con flag disabled, got {sched}"
    print("[OK] DISABLED flag respetado")
    del os.environ["GENOME_REFRESH_DISABLED"]


def test_start_real():
    # Setear delay alto para que NO corra el job en este test.
    os.environ["GENOME_REFRESH_BOOT_DELAY_MIN"] = "9999"  # ~1 semana
    sched = start_genome_refresh_scheduler()
    assert sched is not None, "Esperaba scheduler vivo, got None"
    assert sched.running, "Scheduler no está running"
    jobs = sched.get_jobs()
    assert len(jobs) == 1, f"Esperaba 1 job, got {len(jobs)}"
    job = jobs[0]
    assert job.id == "genome_refresh_recurring", f"Job id inesperado: {job.id}"
    print(f"[OK] Scheduler running con job: {job.id}")
    print(f"     next_run_time: {job.next_run_time}")
    print(f"     trigger: {job.trigger}")
    shutdown_genome_refresh_scheduler(sched)
    print("[OK] Shutdown sin errores")
    del os.environ["GENOME_REFRESH_BOOT_DELAY_MIN"]


if __name__ == "__main__":
    test_disabled()
    test_start_real()
    print("\n[ALL TESTS PASSED]")
