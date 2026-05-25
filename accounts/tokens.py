from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return '{}{}{}{}'.format(
            user.pk,
            timestamp,
            user.email,
            user.is_active,
        )


account_activation_token = AccountActivationTokenGenerator()
