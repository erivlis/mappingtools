"""
Recipe 19: Feature Flag Rollout State (native python + distinct)

In continuous deployment, you often use complex Feature Flags
(e.g., A/B testing, beta rings). When calculating the effective
state for a user, you may need to resolve multiple overlapping flag
evaluations from different tiers (Global -> Region -> User).

This recipe combines native python dictionary comprehensions to isolate
feature flags from a generic user session, and `distinct` to figure out
the unique states of those flags across multiple cohorts.
"""

from mappingtools.operators import distinct


def main():
    # 1. The different tiers of configuration evaluated for a user session.
    # The order of precedence is Global -> Region -> User
    global_flags = {
        "ff_dark_mode": True,
        "ff_new_checkout": False,
        "system_timeout": 300 # Not a feature flag
    }

    region_flags = {
        "ff_new_checkout": True, # Enabled for this region
        "ff_crypto_pay": False,
        "datacenter": "us-east-1" # Not a feature flag
    }

    user_flags = {
        "ff_crypto_pay": True,    # User is in the beta group
        "ff_experimental_ui": True,
        "username": "alice"       # Not a feature flag
    }

    # 2. Extract ONLY the feature flags from the configurations
    # Since `keep` is deprecated, we use a clean native dictionary comprehension.
    def is_feature_flag(key: str) -> bool:
        return key.startswith("ff_")

    flags_only = [
        {k: v for k, v in conf.items() if is_feature_flag(k)}
        for conf in (global_flags, region_flags, user_flags)
    ]

    print("--- 1. Isolated Feature Flag Subsets ---")
    for i, subset in enumerate(flags_only):
        print(f"Tier {i+1}: {subset}")

    # 3. Determine all unique feature flag states a user *might* encounter
    # We use `distinct` to extract every unique value for a specific flag across the cascade
    print("\n--- 2. Distinct Flag States Across Tiers ---")
    flag_keys = {k for subset in flags_only for k in subset}

    for flag in sorted(flag_keys):
        # We pass all three subset dictionaries to `distinct`
        unique_states = list(distinct(flag, *flags_only))
        print(f"Flag '{flag}': {unique_states}")

        # If a flag has more than one state in the cascade, it means there is an override!
        if len(unique_states) > 1:
            print(f"  -> WARNING: '{flag}' is overridden at a lower tier!")


if __name__ == "__main__":
    main()
