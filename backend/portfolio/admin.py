from django.contrib import admin
from .models import (Portfolio, PortfolioApproval, PortfolioTemplate,
                     PortfolioVersion, PortfolioView)

admin.site.register([PortfolioTemplate, Portfolio, PortfolioVersion,
                     PortfolioApproval, PortfolioView])