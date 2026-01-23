from django.test.runner import DiscoverRunner


class AppLabelDiscoverRunner(DiscoverRunner):
    default_labels = [
        "apps.users",
        "apps.projects",
        "apps.documents",
        "apps.wps",
        "apps.wpq",
        "apps.welds",
        "apps.quality",
        "apps.reports",
        "apps.integrations",
    ]

    def run_tests(self, test_labels=None, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = list(self.default_labels)
        return super().run_tests(test_labels, extra_tests=extra_tests, **kwargs)
