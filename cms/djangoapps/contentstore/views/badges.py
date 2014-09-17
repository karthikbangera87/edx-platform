
import badgekit.api

def get_badges(courseID,useremail):
	
	badge_issuer,badge_program,course_run=courseID.split('/')
	badgeobj=badgekit.api.BadgeKitAPI('http://10.0.2.2:5000','hihello',defaults={'system':badgekit})
	badges_available=badgeobj.list('badge',system='badgekit',issuer=badge_issuer,program=badge_program)
	return badges_available 

