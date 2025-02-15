import numpy as np


class AbilityBar:
    """
    The AbilityBar class containing all the properties the Ability Bar has in RuneScape.
    """

    def __init__(self, opt, player, Do):
        self.GCDStatus = False                  # When True, the ability bar is on a global cooldown
        self.GCDTime = 0                        # Time before the global cooldown wears of
        self.GCDMax = 3                         # Maximum time of a global cooldown
        self.Adrenaline = player.MaxAdrenaline  # Amount of adrenaline that has been generated, starting with maximum allowable value
        self.FireStatus = False                 # When True, a chosen ability is allowed to be used
        self.FireN = None                       # The index of the ability to be fired in the current tick
        self.Rotation = []                      # Contains the abilities put on the bar
        self.N = 0                              # Amount of abilities on the bar
        self.AbilNames = []                     # A list of names of abilities on the bar
        self.AbilEquipment = []                 # A list of equipment allowed for using the abilities
        self.AbilStyles = []                    # A list of ability styles
        self.Threshold = 15                     # Adrenaline used for a threshold ability

        self.Basic = 9 if opt['FotS'] else 8                        # Adrenaline generated by a basic ability

        if player.PerkImpatient:
            self.Basic += 3 * 0.09 * player.Ir

        if not player.RoV and not player.CoE:                       # Ultimate adrenaline cost
            self.Ultimate = 100
        elif player.RoV and player.CoE:
            self.Ultimate = 80
        else:
            self.Ultimate = 90

        if Do.HTMLwrite:
            Do.Text += f'<li style="color: {Do.init_color};">User select: Ultimate adrenaline cost: {self.Ultimate}</li>' \
                       f'<li style="color: {Do.init_color};">User select: Basic adrenaline gain: {self.Basic}</li>'

        # Groups of abilities which share a cooldown
        self.SharedCDs = [
            ['Surge', 'Escape'],
            ['Forceful Backhand', 'Stomp', 'Tight Bindings', 'Rout', 'Deep Impact', 'Horror'],
            ['Backhand', 'Kick', 'Binding Shot', 'Demoralise', 'Impact', 'Shock'],
            ['Fragmentation Shot', 'Combust'],
            ['Metamorphosis', 'Sunshine'],
            ['Destroy', 'Hurricane']
        ]

        # Groups of abilities which cannot appear together on the ability bar
        self.Invalid = [
            ['Lesser Smash', 'Smash'],
            ['Lesser Havoc', 'Havoc'],
            ['Lesser Sever', 'Sever'],
            ['Lesser Dismember', 'Dismember'],
            ['Fury', 'Greater Fury'],
            ['Barge', 'Greater Barge'],
            ['Flurry', 'Greater Flurry'],
            ['Lesser Combust', 'Combust'],
            ['Lesser Dragon Breath', 'Dragon Breath'],
            ['Lesser Sonic Wave', 'Sonic Wave'],
            ['Lesser Concentrated Blast', 'Concentrated Blast'],
            ['Lesser Snipe', 'Snipe'],
            ['Lesser Fragmentation Shot', 'Fragmentation Shot'],
            ['Lesser Needle Strike', 'Needle Strike'],
            ['Lesser Dazing Shot', 'Dazing Shot', 'Greater Dazing Shot'],
            ['Ricochet', 'Greater Ricochet'],
            ['Chain', 'Greater Chain']
        ]

    def TimerCheck(self, Do):
        """
        Checks the global cooldown status.
        :param Do: The DoList object
        """

        if self.GCDStatus:
            self.GCDTime -= 1

            if self.GCDTime == 0:
                self.GCDStatus = False

                if Do.HTMLwrite:
                    Do.Text += f'<li style="color: {Do.nor_color};">Global cooldown ended</li>\n'

    def AdrenalineStatus(self, Ability, player):
        """
        Checks if an ability is allowed to fire.
        :param Type: Type of ability (Basic/Threshold/Ultimate)
        :param player: The Player object
        """

        if Ability.Type == 'Basic':
            if Ability.Name == 'Dragon Breath' and player.DragonBreathGain:
                self.Adrenaline += self.Basic + 2
            else:
                self.Adrenaline += self.Basic

            if self.Adrenaline > player.MaxAdrenaline:
                self.Adrenaline = player.MaxAdrenaline

            self.FireStatus = True

        elif Ability.Type == 'Threshold' and self.Adrenaline >= 50:
            self.Adrenaline -= self.Threshold
            self.FireStatus = True

        elif Ability.Type == 'Ultimate' and self.Adrenaline >= 100:
            if player.PerkUltimatums and Ability.Name in {'Overpower', 'Frenzy', 'Unload', 'Omnipower'} and 100 - self.Ultimate < player.Ur * 5:
                self.Adrenaline -= 100 - player.Ur * 5
            else:
                self.Adrenaline -= self.Ultimate
            self.FireStatus = True

        else:
            self.FireStatus = False

    def SharedCooldowns(self, FireAbility, player, Do):
        """
        Check if abilities which share a cooldown have to go on cooldown or not.
        :param FireAbility: The ability activated in the current attack cycle.
        :param player: The player object.
        :param Do: The DoList object.
        """

        for i in range(0, len(self.SharedCDs)):
            if FireAbility.Name in self.SharedCDs[i]:
                # Get the index of the ability in that specific list
                FireAbilityIDX = self.SharedCDs[i].index(FireAbility.Name)
                # Assign the complete list to a new variable
                shared_cooldown_list = self.SharedCDs[i].copy()
                # Pop the fired ability of the list
                shared_cooldown_list.pop(FireAbilityIDX)

                for j in range(0, len(shared_cooldown_list)):  # For every remaining ability in the list
                    if shared_cooldown_list[j] in self.AbilNames:
                        idx = self.AbilNames.index(shared_cooldown_list[j])
                        self.Rotation[idx].cdStatus = True
                        self.Rotation[idx].cdTime = self.Rotation[idx].cdMax
                        player.Cooldown.append(self.Rotation[idx])

                        if Do.HTMLwrite:
                            Do.Text += f'<li style="color: {Do.nor_color};">{self.Rotation[idx].Name} went on cooldown</li>\n'

                # The ability will never occur in 2 groups (would not make sense)
                break
