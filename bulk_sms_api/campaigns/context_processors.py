def company_context(request):
    if request.user.is_authenticated:
        user = request.user
        company = getattr(user, 'company', None)
        if company:
            colors = company.color.split(',')
            logo_url = company.logo.url
            return {
                'company': company,
                'colors': colors,
                'logo_url': logo_url,
            }
    return {}