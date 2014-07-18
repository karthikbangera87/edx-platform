#def badges_available_for_course(course):
    # TODO: really find badges
    #return []
import badgekit.api

def badges_available_for_course():
	a=badgekit.api.BadgeKitAPI('http://10.0.2.2:5000','hihello',defaults={'system':'badgekit'})
	return a.list('badge')

