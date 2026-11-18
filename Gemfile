source "https://rubygems.org"

# EoN 홈페이지(Kyonggi-EoN/kyonggi-eon.github.io)와 같은 Jekyll 버전
gem "jekyll", "~> 4.4"

group :jekyll_plugins do
  gem "jekyll-seo-tag", "~> 2.8"
  gem "jekyll-sitemap", "~> 1.4"
end

# Windows에서 로컬 서버를 띄울 때 필요한 시간대 데이터
platforms :windows, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end
