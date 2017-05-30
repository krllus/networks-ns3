import sys

import ns.applications
import ns.core
import ns.internet
import ns.mobility
import ns.network
import ns.wifi

def SetPosition(node, position):
	mobility = node.GetObject(ns.mobility.MobilityModel.GetTypeId())
	mobility.SetPosition(position)

def GetPosition(node):
	mobility = node.GetObject(ns.mobility.MobilityModel.GetTypeId())
	return mobility.GetPosition()

def AdvancePosition(node):
	pos = GetPosition(node);
	pos.x += 5.0
	if pos.x >= 210.0:
		return
	SetPosition(node, pos)
	ns.core.Simulator.Schedule(ns.core.Seconds(1.0), AdvancePosition, node)

def main(argv):

	ns.core.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_INFO)

	# define a node container
	stations = ns.network.NodeContainer()
	
	# create 3 nodes
	stations.Create(3)

	# chose the element at 0 to be the AP of the wifi network
	ap = stations.Get(0)

	# contruct the wifi devices and the intercommunication channel between these wifi nodes 
	phy = ns.wifi.YansWifiPhyHelper.Default()
	channel = ns.wifi.YansWifiChannelHelper.Default()
	phy.SetChannel(channel.Create())

	# wifi helper
	wifi = ns.wifi.WifiHelper.Default()
	wifi.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211b)
	#wifi.SetRemoteStationManager("ns3::ArfWifiManager")
	wifi.SetRemoteStationManager(
		"ns3::ConstantRateWifiManager", 
		"DataMode", ns.core.StringValue("DsssRate5_5Mbps"))
	#	"DataMode", ns.core.StringValue("wifia-54mbs"))
	
	# SSID of the network
	ssid = ns.wifi.Ssid("wifi-home")

	# wifi Mac
	mac = ns.wifi.NqosWifiMacHelper.Default()
	mac.SetType("ns3::StaWifiMac",
                    "Ssid", ns.wifi.SsidValue(ssid),
                    "ActiveProbing", ns.core.BooleanValue(False))
    
	# network device container
	stationDevices = wifi.Install(phy, mac, stations)

	# configuring type for the AP
	mac.SetType("ns3::ApWifiMac",
                    "Ssid", ns.wifi.SsidValue(ssid),
                    "BeaconGeneration", ns.core.BooleanValue(True),
                    "BeaconInterval", ns.core.TimeValue(ns.core.Seconds(2.5)))
	apDevices = wifi.Install(phy, mac, ap)

	# mobility, I dont know that this does
	mobility = ns.mobility.MobilityHelper()
	mobility.Install(stations)
	ns.core.Simulator.Schedule(ns.core.Seconds(1.0), AdvancePosition, ap)

	#print help(ns.internet.InternetStackHelper)
	stackHelper = ns.internet.InternetStackHelper()
	stack = stackHelper.Install(stations)
	
	#Ipv4 address container
	address = ns.internet.Ipv4AddressHelper()
	address.SetBase(
		ns.network.Ipv4Address("10.1.1.0"),
		ns.network.Ipv4Mask("255.255.255.0"))
	stInterfaces = address.Assign(stationDevices)
	apInterfaces = address.Assign(apDevices)

	device = apDevices.Get(ap.GetId())

	echoServer = ns.applications.UdpEchoServerHelper(9)

	serverApps = echoServer.Install(stations.Get(1))
	serverApps.Start(ns.core.Seconds(1.0))
	serverApps.Stop(ns.core.Seconds(10.0))

	echoClient = ns.applications.UdpEchoClientHelper(stInterfaces.GetAddress(1), 9)
	echoClient.SetAttribute("MaxPackets", ns.core.UintegerValue(1))
	echoClient.SetAttribute("Interval", ns.core.TimeValue(ns.core.Seconds(1.0)))
	echoClient.SetAttribute("PacketSize", ns.core.UintegerValue(1024))

	clientApps = echoClient.Install(stations.Get(2))
	clientApps.Start(ns.core.Seconds(1.0))
	clientApps.Stop(ns.core.Seconds(2.0))

	ns.core.Simulator.Run()
	ns.core.Simulator.Destroy()

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))