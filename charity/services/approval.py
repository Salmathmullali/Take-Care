from charity.constants import ReviewStatus


def approve_profile(profile, admin_message=''):
    profile.status = ReviewStatus.APPROVED
    if admin_message:
        profile.admin_message = admin_message
    profile.save()
    return profile


def reject_profile(profile, admin_message):
    profile.status = ReviewStatus.REJECTED
    profile.admin_message = admin_message
    profile.save()
    return profile
