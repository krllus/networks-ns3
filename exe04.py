import sys

import ns3

import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point

ns.core.LogComponentEnable("V4Ping", ns.core.LOG_LEVEL_INFO)
#ns.core.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_INFO)
#ns.core.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_INFO)

wifiHelper = ns3.WifiHelper()
wifiHelper.SetStandard(ns3.WIFI_PHY_STANDARD_80211b)

wifiChannelHelper = ns3.YansWifiChannelHelper()
wifiChannel = wifiChannelHelper.Default()

wifiPhyHelper = ns3.YansWifiPhyHelper()
wifiPhy = wifiPhyHelper.Default()
wifiPhy.SetChannel(wifiChannel.Create())

nodes = ns.network.NodeContainer()
nodes.Create(2)

mac = ns3.NqosWifiMacHelper.Default()
mac.SetType("ns3::AdhocWifiMac")
 
wifiHelper.SetRemoteStationManager(
	"ns3::ConstantRateWifiManager", 
	"DataMode", ns3.StringValue("DsssRate1Mbps"), 
	"ControlMode", ns3.StringValue("DsssRate1Mbps"))
devices = wifiHelper.Install(wifiPhy,mac,nodes)

olsr = ns3.OlsrHelper()
    
#Add the IPv4 protocol stack to the nodes in our container
internet=ns3.InternetStackHelper()
internet.SetRoutingHelper (olsr)
 
internet.Install (nodes)
ipAddrss= ns3.Ipv4AddressHelper()
ipAddrss.SetBase(
	ns3.Ipv4Address("192.168.0.0"), 
	ns3.Ipv4Mask("255.255.255.0"));
ipContainer = ipAddrss.Assign(devices);

mobility = ns3.MobilityHelper()
positionAlloc = ns3.ListPositionAllocator()
positionAlloc.Add(ns3.Vector (100,100,0.0))
positionAlloc.Add(ns3.Vector (100,200,0.0))

mobility.SetPositionAllocator(positionAlloc)
mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
mobility.Install(nodes)

pingHelper = ns3.V4PingHelper(ipContainer.GetAddress(0))
pingHelper.SetAttribute("Interval", ns3.TimeValue(ns3.Seconds(1.0)))

apps = pingHelper.Install(nodes.Get(0))
apps.Start(ns.core.Seconds(1.0))
apps.Stop(ns.core.Seconds(10.0))

ns.core.Simulator.Run()
ns.core.Simulator.Destroy()