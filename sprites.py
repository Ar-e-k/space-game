class player:

    def __init__(self, x, y, mass, thrust):
        self.x_cord=x
        self.y_cord=y

        self.vertical=0
        self.horizontal=0
        self.modifier=1

        self.vertical_ac=0
        self.horizontal_ac=0

        self.acceleration_mod=thrust/mass

    def move(self):
        self.x_cord+=(self.horizontal*self.modifier)
        self.y_cord+=(self.vertical*self.modifier)

    def update_velocity(self):
        self.vertical+=self.vertical_ac
        self.horizontal+=self.horizontal_ac


    def vertical_thrust(self, direction=1):
        self.vertical_ac+=self.acceleration_mod*direction

    def horixontal_thrust(self, direction=1):
        self.horizontal_ac+=self.acceleration_mod*direction

    def return_cords(self):
        return [self.x_cord, self.y_cord]
