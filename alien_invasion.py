import sys
from time import sleep
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from gamestats import GameStats


class AlienInvasion:
    """This class manages the game behaviours"""

    def __init__(self):
        """Define the game and initialize the game resources"""
        pygame.init()
        self.settings = Settings()
        
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) #This tells pygame to figure out the window size that will fill the screen
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
        self.stats = GameStats(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

    def run_game(self):
        """Start the main loop of the game"""
        while True:
            # Watch for keyboard and mouse events
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                
            self._update_screen()

    def _check_events(self):
        """Respond to key presses and mouse events"""
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()  
                elif event.type == pygame.KEYDOWN:
                    self._check_key_down_events(event)
                        
                elif event.type == pygame.KEYUP:
                    self._check_key_up_events(event)
    
    def _check_key_down_events(self, event):
        """Respond to key presses"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
            
    def _check_key_up_events(self, event):
        """Respond to key releases"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
            
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            
    def _update_bullets(self):
        """Update the position of the bullets and get rid of old bullets"""
        #Update bullet positions
        self.bullets.update()
        #Delete bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
                
        self._check_bullet_alien_collisions()
            
    def _update_screen(self):
        """Update images on the screen and flip to the new screen"""
        self.screen.fill(self.settings.bg_color)
        self.ship.draw_ship()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
            
        self.aliens.draw(self.screen)
        
        pygame.display.flip()
          
    def _create_fleet(self):
        """Create the fleet of alien ships"""
        #Make an alien and find the number of aliens in the row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size 
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_of_aliens_x = available_space_x // (2 * alien_width)
        
        #Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = self.settings.screen_height - (3 * alien_height) - ship_height
        number_rows = available_space_y // (2 * alien_height)
        
        #Create the a full fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_of_aliens_x):
                self._create_alien(alien_number, row_number)
     
    def _create_alien(self, alien_number, row_number):
        #Create an alien and place it in the row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)       
        
    def _update_aliens(self):
        """Check if the fleet is at the edge, then update the positions of all the aliens in the fleet"""
        self._check_fleet_edges()
        self.aliens.update()
        
        #Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            
        #Look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()
        
    def _check_fleet_edges(self):
        """Resond if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions"""
        #Check for bullets that have hit alien ships
        #Get rid of the bullet and the alien ship that it hit
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens ,True, True)
        if not self.aliens:
            #Destroy the existing bullets and create a new fleet
            self.bullets.empty()
            self._create_fleet()
            
    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        if self.stats.ships_left > 0:
            #Decrement ships left
            self.stats.ships_left -= 1
            
            #Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            
            #Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            
            #Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
        
        
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #Treat this as if the ship was hit
                self._ship_hit()
                break

if __name__ == '__main__':
    # Make a game instance and run the game
    ai = AlienInvasion()
    ai.run_game()
