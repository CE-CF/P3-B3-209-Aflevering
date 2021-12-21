import mysql.connector
from mysql.connector import errorcode
import time
import datetime




class Database(object):
    """Database class\n
    Functions:\n
    * Create database = instance_db
    * Create tables   = create_tables
    * Insert query    = insert_query
    *
    
    """

    # Instans of a class
    def __init__(self, name, host, user, password):
        self.name     = name
        self.host     = host
        self.user     = user
        self.password = password
        self.connect  = self.connect_db()
        self.cursor   = self.get_cursor()
        
    # Create database
    def instance_db(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cnx_cursor = conn.cursor()
            cnx_cursor.execute("CREATE DATABASE {}".format(self.name))

        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))    

    # Create tables
    def create_tables(self):
        try:
            self.cursor.execute("CREATE TABLE Room_History (PRIMARY KEY(Time, Room), Time DATETIME(0), Room VARCHAR(50), Room_id TINYINT(1), Temperature DECIMAL(3,1), Humidity TINYINT(1), Motion TINYINT(1))")
            self.cursor.execute("CREATE TABLE Network_History (Time DATETIME(0) PRIMARY KEY, Bits INT UNSIGNED)")
            self.cursor.execute("CREATE TABLE Power_History (PRIMARY KEY(Time, Room_id), TIME DATETIME(0), Room_id TINYINT(1), Power_state TINYINT(1))")
            self.cursor.execute("CREATE TABLE User_Input (Time DATETIME(0), MAC_address VARCHAR(50) PRIMARY KEY, Work_time DECIMAL(4,2), Sleep_time DECIMAL(4,2))")
            self.cursor.execute("CREATE TABLE Current_Status (Time DATETIME(0), Room VARCHAR(50) PRIMARY KEY, Room_id TINYINT(1), Temperature DECIMAL(3,1), Humidity TINYINT(1), Motion TINYINT(1), Bits INT UNSIGNED, Power_State TINYINT(1))")
            
            # Insert default information in table Current Status upon creation. 
            rooms = ('Bathroom', 'Bedroom', 'Garage', 'Kitchen', 'Living room')
            room_id = 1
            for x in rooms:
                query = "INSERT INTO Current_Status (Time, Room, Room_id, Temperature, Humidity, Motion, Bits, Power_State) VALUES (CURRENT_TIME, %s, %s, %s, %s, %s, %s, %s)"
                data = (x, room_id, 0, 0, 0, 0, 1)
                self.cursor.execute(query, data)
                self.connect.commit()
                room_id +=1
            #self.cursor.execute("INSERT INTO Network_History (Time, Bits) VALUES (CURRENT_TIME, 0)")

        except mysql.connector.Error as err:
            print("Failed creating tables: {}".format(err))

    # Reset the entire database
    def reset_entire_database(self):
        try:
            self.cursor.execute("DROP TABLE Room_History")
            self.connect.commit()
            self.cursor.execute("DROP TABLE Power_History")
            self.connect.commit()
            self.cursor.execute("DROP TABLE Network_History")
            self.connect.commit()
            self.cursor.execute("DROP TABLE User_Input")
            self.connect.commit()
            self.cursor.execute("DROP TABLE Current_Status")
            self.connect.commit()
            self.create_tables()
        except:
            self.create_tables()

    # Open connection to database
    def connect_db(self):
        conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.name)
        return conn

    # Create cursor to database
    def get_cursor(self):
        return self.connect.cursor()

    # Close connection to database
    def disconnect_db(self):
        if self.connect.is_connected():
                self.cursor.close()
                self.connect.close()


#? ##########################################################
#? "Little helper" functions 
    # Remake data tuple for update query = puts the first element in the end of the tuple
    def remake_tuple(self, data):
        newtuple = []
        room = data[0]
        for i in data:
            newtuple.append(i)
        newtuple.pop(0)
        newtuple.append(room)
        newtuple = tuple(newtuple)
        return newtuple     

    # Returns True if MAC address exsits in User_Input Table
    def mac_lookup(self, data, table):
        try:
            if table == 'UI':
                self.cursor.execute("SELECT * FROM User_Input")
                mac_address = self.cursor.fetchall()
                for x in mac_address:
                    if x[1] == data[0]:
                        return True
            elif table == 'NH':
                self.cursor.execute("SELECT * FROM User_Input")
                mac_address = self.cursor.fetchall()
                for x in mac_address:
                    if x[1] == data:
                        return True
                    else:
                        continue
                return False    
        except mysql.connector.Error as err:
                print("Failed to lookup MAC in {}: {}".format(table, err))

    # Removes ':' from the mac address and returns the newly redefined mac address
    def redefine_mac_address(self, data):
        new_mac = ''
        mac_chop = data.split(':')
        for x in mac_chop:
            new_mac = new_mac + x
        return new_mac

    # Returns two tuple. One for creation of a column in CS/NH and one for updating it. 
    def _mac_alter_table(self, data, table):
        mac = data[0]
        new_mac = self.redefine_mac_address(mac)
        
        if table == 'CS':
            first_indent = 'ALTER TABLE Current_Status ADD '
            second_indent = new_mac
            third_indent = ' TINYINT(1) DEFAULT 0'
            new_data = first_indent + second_indent + third_indent
        
        elif table == 'NH':
            first_indent = 'ALTER TABLE Network_History ADD '
            second_indent = new_mac
            third_indent = ' TINYINT(1) DEFAULT 0'
            new_data = first_indent + second_indent + third_indent
        
        new_list = []
        new_list.append(1)
        new_list.append(new_mac)
        new_list = tuple(new_list)
        return new_data, new_list

    # Returns room_id for a room
    def room_id_lookup(self, room):
        print(f'Sensor {room}')
        f_str = "SELECT Room_id FROM Current_Status WHERE Room = '"
        l_str = "'"
        query = f_str + room + l_str
        print(f'Sensor {room} query: {query}')
        self.cursor.execute(query)
        room = self.cursor.fetchall()
        print(f'Sensor {room} query response: {room}')
        self.connect.commit()
        room = room[0]
        room_id = int(room[0])
        return room_id
        


#? ################################################################
    #? Query for inserting data into a table
    def insert_query(self, table, data, index = None):
        
    # Insert data into Room History table
        if table == 'RH':
            try:
                room_id = self.room_id_lookup(data[0])
                data = list(data)
                data.insert(1,room_id)
                data = tuple(data)

                query = "INSERT INTO Room_History (Time, Room, Room_id, Temperature, Humidity, Motion) VALUES (CURRENT_TIME, %s, %s, %s, %s, %s)"
                self.cursor.execute(query, data)
                self.connect.commit()
                self.update_query('CS', data)
            except mysql.connector.Error as err:
                print("Failed to insert in {}: {}".format(table, err))
            

    # Insert data into the User Input table
        elif table == 'UI':
            try:
                # if MAC address exsits in Table
                if self.mac_lookup(data, table) == True:
                    self.update_query('UI', data)
                else:
                    # Insert new MAC address into UI table
                    try:  
                        query = "INSERT INTO User_Input (Time, MAC_address, Work_time, Sleep_time) VALUES (CURRENT_TIME, %s, %s, %s)"
                        self.cursor.execute(query, data)
                        self.connect.commit()
                        
                        # Add column for MAC in CS table
                        query, new_mac = self._mac_alter_table(data, 'CS')
                        self.cursor.execute(query)
                        self.connect.commit()

                        # Add column for MAC in NH table
                        query, new_mac = self._mac_alter_table(data, 'NH')
                        self.cursor.execute(query)
                        self.connect.commit()
                    except mysql.connector.Error as err:
                        print("Failed to create new MAC in {}: {}".format(table, err))

            except mysql.connector.Error as err:
                print("Failed to update MAC in {}: {}".format(table, err))
              
    # Insert data into Network History table and update MAC activity in Current Status
        elif table == 'NH':
            try:
                # Then NO mac addresses is registered by the network module
                if len(data) < 2:      
                    first_str = "INSERT INTO Network_History (Time, Bits) VALUES (CURRENT_TIME, "
                    second_str = str(data[0])
                    third_str = ")"
                    query = first_str + second_str + third_str
                    self.cursor.execute(query)
                    self.connect.commit()

                    # Update bits in current status
                    f_str = "UPDATE Current_Status SET Bits = "
                    bits = str(data[0])
                    l_str = " WHERE Room = 'Living room'"
                    query = f_str + bits + l_str
                    self.cursor.execute(query)
                    self.connect.commit()
                    
                    # Sets all mac activity to 0 (zero) in Current Status
                    self.cursor.execute("SELECT * FROM User_Input")
                    mac_address = self.cursor.fetchall()
                    for x in mac_address:
                        self.update_query('NH',x[1],0) 
            
                # One or more mac addresses is registered by the network module
                elif len(data) >= 2:  
                    #TODO Add mac address active i network history
                    # Insert bits in Network_History
                    first_str = "INSERT INTO Network_History (Time, Bits) VALUES (CURRENT_TIME, "
                    second_str = str(data[0])
                    third_str = ")"
                    query = first_str + second_str + third_str
                    self.cursor.execute(query)
                    self.connect.commit()

                    # Update bits in Current_Status
                    f_str = "UPDATE Current_Status SET Bits = "
                    bits = str(data[0])
                    l_str = " WHERE Room = 'Living room'"
                    query = f_str + bits + l_str
                    self.cursor.execute(query)
                    self.connect.commit()

                    # Get all column names
                    self.cursor.execute("SHOW columns FROM Current_Status")
                    column_names = [column[0] for column in self.cursor.fetchall()] 
                    del column_names[0:8]
                    
                    # Update mac address in current status to be active
                    data.pop(0)
                    for x in data:
                        active_mac = self.redefine_mac_address(x)
                        if active_mac in column_names:
                            pop_num = column_names.index(active_mac)
                            self.update_query('NH',active_mac,1)
                            column_names.pop(pop_num)

                    # Update non-active mac address in current status to be non-active
                    for x in column_names:
                        self.update_query('NH',x,0)               
            except mysql.connector.Error as err:
                print("Failed to insert data in {} or update MAC activity in CS: {}".format(table, err))
    
    # Insert data into Power History table
        elif table == 'PH':
            try:
                query = "INSERT INTO Power_History (Time, Room_id, Power_State) VALUES (CURRENT_TIME, %s, %s)"
                self.cursor.execute(query, data)
                self.connect.commit()
                self.update_query('PH',data)
            except mysql.connector.Error as err:
                print("Failed to insert in {}: {}".format(table, err))


#? ###################################################
    #? Query for updating data in table
    def update_query(self, table, data, index=None):
        """Query for updating specific areas within the database.

        Args:
            table (str): Initial for the table. Ex Current Status = CS
            data (tuple): Contains parameters, the tuple size depends on table
            index (int, optional): Special cases. Defaults to None.
        """
        # Update Current Status Table
        if table == 'CS':
            try:
                data = self.remake_tuple(data)
                query = "UPDATE Current_Status SET Time = CURRENT_TIME, Room_id = %s, Temperature = %s, Humidity = %s, Motion = %s WHERE Room = %s"
                self.cursor.execute(query, data)
                self.connect.commit()                
            except mysql.connector.Error as err:
                    print("Failed to update in {}: {}".format(table, err))
        
        # Update User Input Table
        elif table == 'UI':
            try:
                data = self.remake_tuple(data)
                query = "UPDATE User_Input SET Time = CURRENT_TIME, Work_time = %s, Sleep_time = %s WHERE MAC_address = %s"
                self.cursor.execute(query,data)
                self.connect.commit()
            except mysql.connector.Error as err:
                print("Failed to update in {}: {}".format(table, err))
        
        # Update Bits in Current Status
        elif table == 'NH':
            if index == 1:
                try:
                    mac = self.redefine_mac_address(data)
                    f_string = "UPDATE Current_Status SET "
                    l_string = " = 1 WHERE Room = 'Living room'"
                    query = f_string + mac + l_string
                    self.cursor.execute(query)
                    self.connect.commit()
                except mysql.connector.Error as err:
                    print("Failed to update MAC1 activity in CS: {}".format(err))

            elif index == 0:
                try:
                    mac = self.redefine_mac_address(data)
                    f_string = "UPDATE Current_Status SET "
                    l_string = " = 0 WHERE Room = 'Living room'"
                    query = f_string + mac + l_string
                    self.cursor.execute(query)
                    self.connect.commit()
                except mysql.connector.Error as err:
                    print("Failed to update MAC0 activity in CS: {}".format(err))
    
    # Update Power_State in Current_Status
        elif table == 'PH':
            try:
                data =data[::-1]
                query = "UPDATE Current_Status SET Power_State = %s WHERE Room_id = %s"
                self.cursor.execute(query,data)
                self.connect.commit()
            except mysql.connector.Error as err:
                    print("Failed to update Power_State in CS: {}".format(err))


#? ###########################################
    #? Jarvis functions

    # Return motion for all rooms in Current_Status
    def get_motion_data(self):
        try:
            self.cursor.execute("SELECT Motion FROM Current_Status")
            motion = self.cursor.fetchall()
            self.connect.commit()
            motion_data = []
            for x in motion:
                motion_data.append(x[0])
            
            return motion_data
        except mysql.connector.Error as err:
                    print("Failed to get motion data in CS: {}".format(err))

    # Return all registred mac address as strings
    def get_active_mac_str(self):
        try:
            # Locate registered mac address´ in User_Input Table
            self.cursor.execute("SELECT * FROM User_Input")
            mac_address = self.cursor.fetchall()
            self.connect.commit()
            registered_mac = []
            for x in mac_address:
                registered_mac.append(x[1])

            print(f'DB: Checking registered_mac: {registered_mac}')
            return registered_mac
        except mysql.connector.Error as err:
                    print("Failed to check mac activity in CS: {}".format(err))
    # Return True if a registered mac address is active on the network
    def get_active_mac(self):
        try:
            # Locate registered mac address´ in User_Input Table
            self.cursor.execute("SELECT * FROM User_Input")
            mac_address = self.cursor.fetchall()
            self.connect.commit()
            registered_mac = []
            for x in mac_address:
                registered_mac.append(self.redefine_mac_address(x[1]))
            
            # Check if mac address is active on the network
            for x in registered_mac:
                f_str = "SELECT "
                l_str =  " FROM Current_Status WHERE Room = 'Living room'"
                query = f_str + x + l_str
                self.cursor.execute(query)
                activity = self.cursor.fetchone()
                self.connect.commit()
                if activity[0] == 1:
                    return True
                    break
            return False
        except mysql.connector.Error as err:
                    print("Failed to check mac activity in CS: {}".format(err))
    

    # Returns the throughput in bits from Current_Status
    def get_network_bits(self):
        try:
            self.cursor.execute("SELECT Bits FROM Current_Status WHERE Room_id = 5")
            bits = self.cursor.fetchone()
            bits = bits[0]
            return bits
        except mysql.connector.Error as err:
                    print("Failed to get bits in CS: {}".format(err))

    # Returns a list of the time schema of the house
    def get_time_schema(self):
        try:
            self.cursor.execute("SELECT Work_time, Sleep_time FROM User_Input")
            GDPR = self.cursor.fetchall()
            self.connect.commit()
            time_schema = []
            work = []
            sleep = []
            for x in GDPR: 
                work.append(float(x[0]))
                sleep.append(float(x[1]))
            
            # Finds the hour for when the last person leaves the house 
            leave_time = int(work[0])
            for x in work:
                if leave_time < int(x):
                    leave_time = int(x)
                elif leave_time >= int(x):
                    continue
            # Finds the hour for when the first one gets home
            home_time = work[0]- int(work[0])
            for x in work:
                if home_time > (x-int(x)): 
                    home_time = (x-int(x))
                elif home_time <= (x-int(x)):
                    continue

            time_schema.append(leave_time + home_time)
            
            # Finds the hour for when the lase person go to bed. Based on everyone goes to bed before midnight (00.00)
            sleep_time = int(sleep[0])
            for x in sleep:
                if sleep_time < int(x):
                    sleep_time = int(x)
                elif sleep_time >= int(x):
                    continue

            wake_time = sleep[0]- int(sleep[0])
            for x in sleep:
                if wake_time > (x-int(x)): 
                    wake_time = (x-int(x))
                elif wake_time <= (x-int(x)):
                    continue

            time_schema.append(sleep_time + wake_time)
            return time_schema
        except mysql.connector.Error as err:
            print("Failed to get time schema: {}".format(err))

    # Informs the database a room has been turn on or off
    def power_room(self, room_id, power_state):
        data = (room_id,power_state)
        self.insert_query('PH',data)

        # ! Commit was missing here 
        
        self.connect.commit()
        return True

    # Informs the database the house has been turn on or off
    def power_house(self, state):
        for x in range(1,6):
            data = (x, state)
            self.insert_query('PH',data)
            
            # ! Commit was missing here 
            
            self.connect.commit()
        return True

#? ###########################################
    #? User Interface functions

    # Returns the power state from Current_Status table.
    def get_power_state(self):
        try:
            self.cursor.execute("SELECT Power_State FROM Current_Status")
            state = self.cursor.fetchall()
            self.connect.commit()
            room_state = []
            for x in state:
                data = list(x)
                room_state.append(int(data[0]))
            print(f'DB: room_state {room_state}')
            return room_state
        except mysql.connector.Error as err:
                    print("Failed to get power state in CS: {}".format(err))

    # Returns the user information about all registered users.
    def get_user_data(self):
        try:
            self.cursor.execute("SELECT * FROM User_Input")
            GDPR = self.cursor.fetchall()
            GDPR_shh = []
            GDPR_we_know = []
            for x in GDPR:
                GDPR_we_know.append(x[0])
                GDPR_we_know.append(str(x[1]))
                GDPR_we_know.append(float(x[2]))
                GDPR_we_know.append(float(x[3]))
                GDPR_shh.append(GDPR_we_know)
                GDPR_we_know = []
            return GDPR_shh
        except mysql.connector.Error as err:
                    print("Failed to get user info in UI: {}".format(err))

    # Returns two listed lists for the last 2 hours. First one for Room_History, next one for Power_History
    def get_plot_data(self, room):
        try:
            # Create tuple for query
            hours_to_substract = 2
            now = datetime.datetime.now()
            now = now.replace(microsecond = 0)
            earlier_datetime = now - datetime.timedelta(hours = hours_to_substract)
            room_id = self.room_id_lookup(room)
            
            data = (room_id, earlier_datetime)

            # Extract data from Room_History 
            query = "SELECT Time, Temperature, Humidity FROM Room_History WHERE Room_id = %s ORDER BY Time >= %s"
            self.cursor.execute(query, data)
            history_data = self.cursor.fetchall()
            self.connect.commit()
            time_frame = []
            time_line_data = []
            i = 0

            # Convert data from Room_History
            for x in history_data:
                time_frame.append(x[0])
                time_frame.append(float(x[1]))
                time_frame.append(int(x[2]))
                time_line_data.append(time_frame)
                time_frame = []
                i += 1
            
            # Extract data from Power_History
            query = "SELECT Time, Power_State FROM Power_History WHERE Room_id = %s ORDER BY Time >= %s"
            self.cursor.execute(query, data)
            power_data = self.cursor.fetchall()
            self.connect.commit()

            return time_line_data, power_data
        except mysql.connector.Error as err:
                    print("Failed to get data for UI plot: {}".format(err))


#? Program begins here
if __name__ == '__main__':

    db = Database('DB','localhost','admin','root')
    #db.create_tables()
    """
    #! When sensor insert data into Room History
    #! Data is a tuple with (Room name, Temperature, Humidity, Motion)
    data = ("Bathroom", 20.7, 95, 1)
    db.insert_query("RH", data)
    data = ("Bedroom", 19, 70, 0)
    db.insert_query("RH", data)
    data = ("Garage", 17.8, 60, 0)
    db.insert_query("RH", data)
    data = ("Kitchen", 19.8, 82, 1)
    db.insert_query("RH", data)
    data = ("Living room", 20.2, 78, 1)
    db.insert_query("RH", data)
    time.sleep(3)

    data = ('B4:1A:1D:E1:1F:ED', 7.16, 22.06)
    db.insert_query("UI", data)
    """
    """
    data = ("Bathroom", 20.5, 90, 1)
    db.insert_query("RH", data)
    data = ("Bedroom", 20, 60, 0)
    db.insert_query("RH", data)
    data = ("Garage", 16.8, 60, 1)
    db.insert_query("RH", data)
    data = ("Kitchen", 18.8, 57, 0)
    db.insert_query("RH", data)
    data = ("Living room", 19.1, 65, 1)
    db.insert_query("RH", data)
    
    #! When UI insert info to User Input
    #! Data is a tuple with (MAC address, Work time, Sleep time)
    data = ('00:1A:C2:7B:00:50', 8.15, 00.06)
    db.insert_query("UI", data)
    
    data = ('G7:1A:Y2:4T:80:40', 7.16, 22.06)
    db.insert_query("UI", data)

    data = ('K2:6E:X5:9D:65:15', 6.16, 21.05)
    db.insert_query("UI", data)
    
    data = ('U2:5Y:W8:1B:37:56', 9.17, 23.08)
    db.insert_query("UI", data)

    #! When the network monitor insert data to Network
    #! Data is a tuple with (Bits, MAC(if any exsits))
    data = [11524]
    db.insert_query('NH', data)
    """
    """
    time.sleep(1)
    data = [854662,'G7:1A:Y2:4T:80:40']
    db.insert_query('NH', data)
    time.sleep(1)
    data = [854662,'G7:1A:Y2:4T:80:40','YY:XX:YY:XX:YY:XX']
    db.insert_query('NH', data)
    time.sleep(1)
    data = [42534000,'00:1A:C2:7B:00:50','G7:1A:Y2:4T:80:40']
    db.insert_query('NH', data)
    
    
    #! When the power is turned on or off in a room
    #! Data is a tuple with (Room_id, Power_state)
    data = (1,0)
    db.insert_query('PH',data)
    data = (2,1)
    db.insert_query('PH',data)
    data = (3,0)
    db.insert_query('PH',data)
    data = (4,1)
    db.insert_query('PH',data)
    data = (5,0)
    db.insert_query('PH',data)   
    """

    db.reset_entire_database()
    db.disconnect_db()