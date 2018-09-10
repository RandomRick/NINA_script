$port = New-Object System.IO.Ports.SerialPort COM9,115200,None,8,one
$vars = New-Object StaticVars

function MainFunc () {
    Try
    {
        $vars::transactioncount  = 1
        cls
        $port.Open()
        $port.DiscardInBuffer()
        $port.ReadTimeout=30000
        #Start-Sleep -Milliseconds 250
    
        #WriteRead ("AT+UFACTORY")
        WriteRead ("AT+UBTCM=2")
        WriteRead ("AT+UBTDM=3")
        WriteRead ("AT+UBTPM=2")
        WriteRead ("AT+UBTLE=2")                    # 2 is peripheral
        WriteRead ("AT+UDSC=0,0")                   # turn off SPS server to increase GATT characteristics capability
        WriteRead ("AT+UBTLECFG=26,2")              # fiddle with MTU size - as above.
        WriteRead ("AT+UBTLN=""REFCOperipheralserver""")
        WriteRead ("AT+UBTLEDIS=REFCO_Ltd,CLA,6.12,1")
        WriteRead ("AT&W")                          # reset 1
        WriteRead ("AT+CPWROFF")                    # reset 2
		# set up device information service
        WriteRead ("AT+UBTGSER=180A")               # service (180A = Device Info)
        WriteRead ("AT+UBTGCHA=2A23,10,1,1")        # characteristic System ID
        WriteRead ("AT+UBTGCHA=2A24,10,1,1")        # characteristic Model Number String
        WriteRead ("AT+UBTGCHA=2A25,10,1,1")        # characteristic Serial Number String
#        WriteRead ("AT+UBTGCHA=2A26,10,1,1")        # characteristic Firmware Revision String
#        WriteRead ("AT+UBTGCHA=2A27,10,1,1")        # characteristic Hardware Revision String
        WriteRead ("AT+UBTGCHA=2A29,10,1,1")        # characteristic Manufacturer Name String
        #WriteRead ("AT+UBTGSN=50,77")      # Mfg Name String

        # setup device data service  # use UUID without connecting line
        WriteRead ("AT+UBTGSER=b0897c037fdd42a499abef47e3fe574f")
#        WriteRead ("AT+UBTGCHA=34832c10687d4eedb17f8b14f5ce70ea,10,1,1")        # Device State
#        WriteRead ("AT+UBTGCHA=854abe1146474a598fd2062278a6b691,10,1,1")        # Device Alarms
#        WriteRead ("AT+UBTGCHA=efa28478f59f431b832c89df618f4de2,10,1,1")        # Reader Time Period
#        WriteRead ("AT+UBTGCHA=5136a9ae032d4f16a9462a062abf6b85,10,1,1")        # Number of Connected Devices
#        WriteRead ("AT+UBTGCHA=7e6613f156fe46719c01f6605d5643f5,10,1,1")        # Transmitter Power (error in GATT definition confusing TX Power with RSSI)
#        WriteRead ("AT+UBTGCHA=775bf19859854a7596e32001ca1eba83,10,1,1")        # URL
        WriteRead ("AT+UBTGCHA=a76f5dc0ba6648a5b5db193f77bf9cdb,10,1,1")        # Refrigerant Name
#        WriteRead ("AT+UBTGCHA=2a840c865ad742d6b0d0733ff134c215,10,1,1")        # Device Temperature Unit
#        WriteRead ("AT+UBTGCHA=3967993db8f84cacbddf65c38e452592,10,1,1")        # Device Pressure Unit
#        WriteRead ("AT+UBTGCHA=c124f471567d40e89d7a761dd2731fa7,10,1,1")        # Device Vacuum Unit
#        WriteRead ("AT+UBTGCHA=979916f01fcd4bb89f79947cc0537f4d,10,1,1")        # Device Weight Unit
#        WriteRead ("AT+UBTGCHA=e780891363cb46b79898faa82dd4308f,10,1,1")        # Device Rotational Speed Unit
#        WriteRead ("AT+UBTGCHA=0af20aa48de1424da2dfc908b7f27b96,10,1,1")        # Device Valve Status
        WriteRead ("AT+UBTGCHA=dd5ef8d7f96a42d4ba4cf4028a7232f5,10,1,1")        # Device Temperature 1 Value
        WriteRead ("AT+UBTGCHA=d4246dc425a040e0b34f45655882aa05,10,1,1")        # Device Temperature 2 Value
        WriteRead ("AT+UBTGCHA=a4ac522539734fb987e5e8d86ff0a528,10,1,1")        # Device Pressure 1 Value
        WriteRead ("AT+UBTGCHA=87395d5d16774d6daa5a8242614c09d6,10,1,1")        # Device Pressure 2 Value
        WriteRead ("AT+UBTGCHA=ef6111aec3ed4925af6e2f4c7183774b,10,1,1")        # Device Vacuum Value
#        WriteRead ("AT+UBTGCHA=95ab2f3ccc0640d0a23741c3a9f0ac40,10,1,1")        # Device Weight Value
#        WriteRead ("AT+UBTGCHA=c31201094d5e4d4b848de80ad27aa91e,10,1,1")        # Device Rotatational Speed Value
#        WriteRead ("AT+UBTGCHA=bcbacc6c2c394d40ae3fc158c7216ec8,10,1,1")        # Device Set Value
        WriteRead ("AT+UBTGCHA=619b13b76fb1492a98a24fdfb85970c7,10,1,1")        # Device Date
        WriteRead ("AT+UBTGCHA=271cb57aa96c44e382eddb9443591c27,10,1,1")        # Device Time
        # setup  battery service
        WriteRead ("AT+UBTGSER=180F")                                           # Battery Service
        WriteRead ("AT+UBTGCHA=2A19,10,1,1")                                    # Battery Level
		
		#Here we want to connect with a smartphone or an other ble device
		ConnectGatt("")
		
		# Write Values
		"`r"
		Write("***Wait 5s***")
		"`r"
		Start-Sleep -Milliseconds 5000
		WriteRead("AT+UBTGSN=0,24,Adff15091988")								#Write refrigerant data



    
    }
    Catch
    {
    Write ("Caught:")
        Write ($error[2])
    }
    Finally
    {
        Write ("Closing port")
        $port.close()
    }
}



function WriteRead ([string] $stringIn)
{
    "`r"
    Write ("Transaction " + $vars::transactioncount)
    $vars::transactioncount++
    Write ("OUT: " + $stringIn)
    #Start-Sleep -Milliseconds 250
    $port.Write($stringIn + "`r")
    #Start-Sleep -Milliseconds 250
    do
    {
        $Answer = $port.ReadLine()
        Write ("IN:  " + $Answer)
    } until (($Answer -like "OK*") -or ($Answer -like "ERROR*"))
    #if ($Answer -like "ERROR*") {Exit}


#    Write ("IN:  " + $port.ReadLine())
#    Write ("IN:  " + $port.ReadLine())
}

function ConnectGatt()
{
	"`r"
    Write ("Transaction " + $vars::transactioncount)
    $vars::transactioncount++
	"`r"
	Write ("***Please Connect the Smartphone with REFCOperipheralserver***")
	"`r"
	do{
	$Connection = $port.ReadLine()
	Write ("IN:  " + $Connection)
    } until ($Connection -like "+UUBTGRR:*")
	
}


function ListCOMPorts()
{
    Write ("These are the open ports:")
    [System.IO.Ports.SerialPort]::GetPortNames()
}

MainFunc


Class StaticVars
{
    static [int]$transactioncount = 1
}
