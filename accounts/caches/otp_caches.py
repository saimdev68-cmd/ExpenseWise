from django.core.cache import cache
import time
from typing import Optional


class OTPCache:
    """
    Utility class for managing OTP-related cache operations.

    Features:
    - OTP Storage
    - OTP Request Cooldown
    - IP Rate Limiting
    - IP Blocking
    - OTP Verification Attempts
    - OTP Verification Blocking
    """

    # ==========================================================================
    # CACHE CONFIGURATION
    # ==========================================================================

    OTP_EXPIRATION_SECONDS = 600

    OTP_REQUEST_COOLDOWN_SECONDS = 60

    IP_OTP_WINDOW_SECONDS = 600
    MAX_OTP_REQUESTS_PER_IP = 10

    MAX_OTP_VERIFICATION_ATTEMPTS = 3
    OTP_VERIFICATION_BLOCK_SECONDS = 120

    LOGIN_IP_BLOCK_SECONDS = 600

    # ==========================================================================
    # CACHE KEY BUILDERS
    # ==========================================================================

    @staticmethod
    def get_otp_cache_key(email: str, purpose: str) -> str:
        return f"otp:{email}:{purpose}"

    @staticmethod
    def get_otp_cooldown_cache_key(ip: str, email: str) -> str:
        return f"otp_cooldown:{ip}:{email}"

    @staticmethod
    def get_ip_cooldown_cache_key(ip: str) -> str:
        return f"ip_cooldown:{ip}"

    @staticmethod
    def get_ip_otp_request_count_cache_key(ip: str) -> str:
        return f"ip_otp_request_count:{ip}"

    @staticmethod
    def get_ip_block_cache_key(ip: str) -> str:
        return f"ip_block:{ip}"

    @staticmethod
    def get_otp_attempt_cache_key(ip: str, email: str) -> str:
        return f"otp_attempt:{ip}:{email}"

    @staticmethod
    def get_otp_verification_block_cache_key(ip: str, email: str) -> str:
        return f"otp_verification_block:{ip}:{email}"


    # ==========================================================================
    # OTP CACHE
    # ==========================================================================

    @classmethod
    def store_otp(cls, email: str, purpose: str, otp: str) -> None:
        cache.set(
            cls.get_otp_cache_key(email, purpose),
            otp,
            timeout=cls.OTP_EXPIRATION_SECONDS
        )

    @classmethod
    def retrieve_otp(cls, email: str, purpose: str) -> Optional[str]:
        return cache.get(cls.get_otp_cache_key(email, purpose))

    @classmethod
    def remove_otp(cls, email: str, purpose: str) -> None:
        cache.delete(cls.get_otp_cache_key(email, purpose))

    # ==========================================================================
    # OTP REQUEST COOLDOWN
    # ==========================================================================

    @classmethod
    def store_otp_cooldown(cls, ip: str, email: str) -> None:
        expires_at = time.time() + cls.OTP_REQUEST_COOLDOWN_SECONDS

        cache.set(
            cls.get_otp_cooldown_cache_key(ip, email),
            expires_at,
            timeout=cls.OTP_REQUEST_COOLDOWN_SECONDS
        )

    @classmethod
    def retrieve_otp_cooldown_expiry(cls, ip: str, email: str):
        return cache.get(cls.get_otp_cooldown_cache_key(ip, email))

    @classmethod
    def get_remaining_otp_cooldown_seconds(cls, ip: str, email: str) -> int:
        expires_at = cls.retrieve_otp_cooldown_expiry(ip, email)

        if expires_at is None:
            return 0

        return max(int(expires_at - time.time()), 0)

    @classmethod
    def remove_otp_cooldown(cls, ip: str, email: str) -> None:
        cache.delete(cls.get_otp_cooldown_cache_key(ip, email))

    # ==========================================================================
    # IP COOLDOWN
    # ==========================================================================

    @classmethod
    def store_ip_cooldown(cls, ip: str) -> None:
        expires_at = time.time() + cls.IP_OTP_WINDOW_SECONDS

        cache.set(
            cls.get_ip_cooldown_cache_key(ip),
            expires_at,
            timeout=cls.IP_OTP_WINDOW_SECONDS
        )

    @classmethod
    def retrieve_ip_cooldown_expiry(cls, ip: str):
        return cache.get(cls.get_ip_cooldown_cache_key(ip))

    @classmethod
    def get_remaining_ip_cooldown_seconds(cls, ip: str) -> int:
        expires_at = cls.retrieve_ip_cooldown_expiry(ip)

        if expires_at is None:
            return 0

        return max(int(expires_at - time.time()), 0)

    @classmethod
    def remove_ip_cooldown(cls, ip: str) -> None:
        cache.delete(cls.get_ip_cooldown_cache_key(ip))

    # ==========================================================================
    # IP OTP REQUEST COUNTER
    # ==========================================================================

    @classmethod
    def increment_ip_otp_request_count(cls, ip: str) -> int:
        key = cls.get_ip_otp_request_count_cache_key(ip)

        count = cache.get(key, 0) + 1

        cache.set(
            key,
            count,
            timeout=cls.IP_OTP_WINDOW_SECONDS
        )

        return count

    @classmethod
    def retrieve_ip_otp_request_count(cls, ip: str) -> int:
        return cache.get(
            cls.get_ip_otp_request_count_cache_key(ip),
            0
        )

    @classmethod
    def remove_ip_otp_request_count(cls, ip: str) -> None:
        cache.delete(cls.get_ip_otp_request_count_cache_key(ip))

    # ==========================================================================
    # IP BLOCK
    # ==========================================================================

    @classmethod
    def store_ip_block(cls, ip: str) -> None:
        cache.set(
            cls.get_ip_block_cache_key(ip),
            True,
            timeout=cls.IP_OTP_WINDOW_SECONDS
        )

    @classmethod
    def retrieve_ip_block(cls, ip: str):
        return cache.get(cls.get_ip_block_cache_key(ip))

    @classmethod
    def remove_ip_block(cls, ip: str) -> None:
        cache.delete(cls.get_ip_block_cache_key(ip))

    # ==========================================================================
    # OTP VERIFICATION ATTEMPTS
    # ==========================================================================

    @classmethod
    def increment_otp_verification_attempts(cls, ip: str, email: str) -> int:
        key = cls.get_otp_attempt_cache_key(ip, email)

        attempts = cache.get(key, 0) + 1

        cache.set(
            key,
            attempts,
            timeout=cls.OTP_VERIFICATION_BLOCK_SECONDS
        )

        return attempts

    @classmethod
    def retrieve_otp_verification_attempts(cls, ip: str, email: str) -> int:
        return cache.get(
            cls.get_otp_attempt_cache_key(ip, email),
            0
        )

    @classmethod
    def remove_otp_verification_attempts(cls, ip: str, email: str) -> None:
        cache.delete(cls.get_otp_attempt_cache_key(ip, email))

    # ==========================================================================
    # OTP VERIFICATION BLOCK
    # ==========================================================================

    @classmethod
    def store_otp_verification_block(cls, ip: str, email: str) -> None:
        expires_at = time.time() + cls.OTP_VERIFICATION_BLOCK_SECONDS

        cache.set(
            cls.get_otp_verification_block_cache_key(ip, email),
            expires_at,
            timeout=cls.OTP_VERIFICATION_BLOCK_SECONDS
        )

    @classmethod
    def retrieve_otp_verification_block(cls, ip: str, email: str):
        return cache.get(
            cls.get_otp_verification_block_cache_key(ip, email)
        )

    @classmethod
    def get_remaining_otp_verification_block_seconds(
        cls,
        ip: str,
        email: str
    ) -> int:

        expires_at = cls.retrieve_otp_verification_block(ip, email)

        if expires_at is None:
            return 0

        return max(int(expires_at - time.time()), 0)

    @classmethod
    def remove_otp_verification_block(cls, ip: str, email: str) -> None:
        cache.delete(
            cls.get_otp_verification_block_cache_key(ip, email)
        )

    # ==========================================================================
    # CLEAR OTP CACHE
    # ==========================================================================

    @classmethod
    def clear_user_otp_cache(
        cls,
        ip: str,
        email: str,
        purpose: str
    ) -> None:
        cls.remove_otp(email, purpose)
        cls.remove_otp_cooldown(ip, email)
        cls.remove_otp_verification_attempts(ip, email)
        cls.remove_otp_verification_block(ip, email)