#!/usr/bin/env python3
"""
Show all available sport commands
"""

from go2_webrtc_driver.constants import SPORT_CMD, RTC_TOPIC

print("=" * 60)
print("Available Sport Commands")
print("=" * 60)

for cmd_name, cmd_id in SPORT_CMD.items():
    print(f"  {cmd_name}: {cmd_id}")

print("\n" + "=" * 60)
print("Available RTC Topics")
print("=" * 60)

for topic_name, topic_value in RTC_TOPIC.items():
    print(f"  {topic_name}: {topic_value}")

print("\n" + "=" * 60)
