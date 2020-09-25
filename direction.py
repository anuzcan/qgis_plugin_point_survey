import math 

class direction:
	def __init__(self, p1, p2, rotation=0, clockwise=False):
		self.p1 = p1
		self.p2 = p2
		self.rotation = rotation
		self.clockwise = clockwise

	def distance(self):
		return math.sqrt((self.p2[0] - self.p1[0])**2 + (self.p2[1] - self.p1[1])**2)

	def angle_to(self):
		if abs(self.rotation) > 360:
			self.rotation %= 360

		Dx = self.p2[0] - self.p1[0]
		Dy = self.p2[1] - self.p1[1]
		angle = math.degrees(math.atan2(Dx, Dy))

		if self.clockwise:
			angle -= self.rotation
			return angle if angle > 0 else angle + 360
		else:
			angle = (360 - angle if angle > 0 else -1 * angle) - self.rotation
			return angle if angle > 0 else angle + 360

def point_pos(origin, amplitude, angle, rotation=0, clockwise=False):
	if abs(rotation) > 360:
		rotation %= 360
	if clockwise:
		rotation *= -1
	if clockwise:
		angle -= rotation
		angle = angle if angle > 0 else angle + 360
	else:
		angle = (360 - angle if angle > 0 else -1 * angle) - rotation
		angle = angle if angle > 0 else angle + 360

	theta_rad = math.radians(angle)
	return int(origin[0] + amplitude * math.sin(theta_rad)), int(origin[1] + amplitude * math.cos(theta_rad))


# https://stackoverrun.com/es/q/10271498