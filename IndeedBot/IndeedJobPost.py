class IndeedJobPost(object):
    def __init__(self, title="", company_name="", company_loc="", rating_num=0.0, href="", onsite=True,
                 date=None, applied=False):
        self.title = title
        self.company_name = company_name
        self.company_loc = company_loc
        self.rating_num = rating_num
        self.href = href
        self.onsite = onsite
        self.date = date
        self.applied = applied

    def asdict(self):
        return {'title': self.title, 'company_name': self.company_name,
                'company_loc': self.company_loc, 'rating_num': self.rating_num, 'href': self.href,
                'onsite': self.onsite, 'date': self.date, 'applied': self.applied}
