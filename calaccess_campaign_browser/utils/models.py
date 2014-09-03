from django.db import models
from django.template.defaultfilters import title


class AllCapsNameMixin(models.Model):
    """
    Abstract model with name cleaners we can reuse across models.
    """
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.clean_name

    @property
    def short_name(self, character_limit=60):
        if len(self.clean_name) > character_limit:
            return self.clean_name[:character_limit] + "..."
        return self.clean_name

    @property
    def clean_name(self):
        """
        A cleaned up version of the ALL CAPS names that are provided by
        the source data.
        """
        n = self.name
        n = n.strip()
        n = n.lower()
        n = title(n)
        n = n.replace("A. D.", "A.D.")
        force_lowercase = ['Of', 'For', 'To', 'By']
        for fl in force_lowercase:
            s = []
            for p in n.split(" "):
                if p in force_lowercase:
                    s.append(p.lower())
                else:
                    s.append(p)
            n = " ".join(s)
        force_uppercase = [
            'Usaf', 'Pac', 'Ca', 'Ad', 'Rcc', 'Cdp', 'Aclu',
            'Cbpa-Pac'
        ]
        for fl in force_lowercase:
            s = []
            for p in n.split(" "):
                if p in force_uppercase:
                    s.append(p.upper())
                else:
                    s.append(p)
            n = " ".join(s)
        n = n.replace("Re-Elect", "Re-elect")
        n = n.replace("Political Action Committee", "PAC")
        return n
