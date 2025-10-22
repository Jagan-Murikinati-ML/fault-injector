import datetime
import time
import logging
from typing import Any, Dict, Optional
from chaoslib.types import Secrets
from chaosk8s.chaosmesh.stress.actions import stress_memory, delete_stressor
 
__all__ = ["stress_memory_continuous"]
logger = logging.getLogger("chaostoolkit")
 
def stress_memory_continuous(
    name: str = "memory-stress",
    workers: Optional[int] = 1,
    size: Optional[str] = "512MB",
    oom_score: Optional[int] = 1000,
    time_to_get_to_size: Optional[str] = "1s",
    label_selectors: Optional[str] = None,
    mode: str = "all",
    ns: str = "default",
    interval: int = 5,  # ✅ Your custom parameter (seconds between stress cycles)
    duration: int = 300,  # ✅ Your custom parameter (total runtime in seconds)
    stress_duration: str = "3s",  # Duration of each stress cycle
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Continuously apply memory stress at specified intervals to trigger OOMKilled events.
 
    Parameters:
    - interval: Time between stress cycles (seconds)
    - duration: Total time to run the experiment (seconds)
    - stress_duration: How long each stress cycle lasts
    - size: Memory size to stress (should exceed pod memory limit for OOM)
    - All other parameters same as stress_memory
    """
    print(f"🚀 Starting continuous memory stress experiment")
    print(f"📅 Interval: {interval} seconds")
    print(f"⏱️  Duration: {duration} seconds")
    print(f"💾 Memory size: {size}")
    print(f"🎯 Target: {label_selectors}")
    print(f"📍 Namespace: {ns}")
    print(f"⚡ OOM Score: {oom_score}")
 
    start_time = time.time()
    stress_count = 0
    current_stress_name = None
 
    while time.time() - start_time < duration:
        stress_count += 1
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
        print(f"\n{'='*50}")
        print(f"🔥 Memory Stress #{stress_count} at {current_time}")
        print(f"{'='*50}")
 
        try:
            # Delete previous stress if exists
            if current_stress_name:
                try:
                    delete_stressor(current_stress_name, ns, secrets)
                    print(f"🧹 Cleaned up previous stress: {current_stress_name}")
                except Exception as e:
                    print(f"⚠️ Could not delete previous stress: {e}")
 
            # Create new stress cycle
            current_stress_name = f"{name}-cycle-{stress_count}"
 
            result = stress_memory(
                name=current_stress_name,
                workers=workers,
                size=size,
                oom_score=oom_score,
                time_to_get_to_size=time_to_get_to_size,
                ns=ns,
                label_selectors=label_selectors,
                mode=mode,
                duration=stress_duration,
                secrets=secrets
            )
            print(f"✅ Successfully created memory stress: {current_stress_name}")
           # print(f"📊 Stress details: {result}")
 
        except Exception as e:
            print(f"❌ Error during stress #{stress_count}: {e}")
 
        # Calculate remaining time
        elapsed = time.time() - start_time
        remaining = duration - elapsed
 
        # Check if we should continue
        if remaining <= interval:
            print(f"⏰ Less than {interval} seconds remaining, stopping experiment")
            break
 
        # Wait for the interval
        print(f"⏳ Waiting {interval} seconds until next stress cycle...")
        print(f"📊 Time remaining: {remaining:.0f} seconds")
        time.sleep(interval)
 
    # Clean up the last stress cycle
    if current_stress_name:
        try:
            delete_stressor(current_stress_name, ns, secrets)
            print(f"🧹 Final cleanup: {current_stress_name}")
        except Exception as e:
            print(f"⚠️ Could not delete final stress: {e}")
 
    total_duration = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"🏁 Memory Stress Experiment Completed!")
    print(f"{'='*50}")
    print(f"📈 Total stress cycles performed: {stress_count}")
    print(f"⏱️  Total duration: {total_duration:.0f} seconds")
    print(f"📊 Average interval: {total_duration/stress_count:.1f} seconds" if stress_count > 0 else "No stress cycles performed")
 
    return {
        "stress_count": stress_count,
        "duration": total_duration,
        "status": "completed",
        "target": label_selectors,
        "namespace": ns,
        "memory_size": size,
        "oom_score": oom_score
    }
