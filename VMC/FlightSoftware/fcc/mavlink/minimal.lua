-- Wireshark dissector for the MAVLink protocol (please see http://qgroundcontrol.org/mavlink/start for details) 

unknownFrameBeginOffset = 0
local bit = require "bit32"
mavlink_proto = Proto("mavlink_proto", "MAVLink protocol")
f = mavlink_proto.fields

-- from http://lua-users.org/wiki/TimeZone
local function get_timezone()
    local now = os.time()
    return os.difftime(now, os.time(os.date("!*t", now)))
end
local signature_time_ref = get_timezone() + os.time{year=2015, month=1, day=1, hour=0}

payload_fns = {}

messageName = {
    [0] = 'HEARTBEAT',
}

f.magic = ProtoField.uint8("mavlink_proto.magic", "Magic value / version", base.HEX)
f.length = ProtoField.uint8("mavlink_proto.length", "Payload length")
f.incompatibility_flag = ProtoField.uint8("mavlink_proto.incompatibility_flag", "Incompatibility flag")
f.compatibility_flag = ProtoField.uint8("mavlink_proto.compatibility_flag", "Compatibility flag")
f.sequence = ProtoField.uint8("mavlink_proto.sequence", "Packet sequence")
f.sysid = ProtoField.uint8("mavlink_proto.sysid", "System id", base.HEX)
f.compid = ProtoField.uint8("mavlink_proto.compid", "Component id", base.HEX)
f.msgid = ProtoField.uint24("mavlink_proto.msgid", "Message id", base.HEX)
f.payload = ProtoField.uint8("mavlink_proto.payload", "Payload", base.DEC, messageName)
f.crc = ProtoField.uint16("mavlink_proto.crc", "Message CRC", base.HEX)
f.signature_link = ProtoField.uint8("mavlink_proto.signature_link", "Link id", base.DEC)
f.signature_time = ProtoField.absolute_time("mavlink_proto.signature_time", "Time")
f.signature_signature = ProtoField.bytes("mavlink_proto.signature_signature", "Signature")
f.rawheader = ProtoField.bytes("mavlink_proto.rawheader", "Unparsable header fragment")
f.rawpayload = ProtoField.bytes("mavlink_proto.rawpayload", "Unparsable payload")

f.HEARTBEAT_type = ProtoField.uint8("mavlink_proto.HEARTBEAT_type", "type (uint8)")
f.HEARTBEAT_autopilot = ProtoField.uint8("mavlink_proto.HEARTBEAT_autopilot", "autopilot (uint8)")
f.HEARTBEAT_base_mode = ProtoField.uint8("mavlink_proto.HEARTBEAT_base_mode", "base_mode (uint8)")
f.HEARTBEAT_custom_mode = ProtoField.uint32("mavlink_proto.HEARTBEAT_custom_mode", "custom_mode (uint32)")
f.HEARTBEAT_system_status = ProtoField.uint8("mavlink_proto.HEARTBEAT_system_status", "system_status (uint8)")
f.HEARTBEAT_mavlink_version = ProtoField.uint8("mavlink_proto.HEARTBEAT_mavlink_version", "mavlink_version (uint8)")

-- dissect payload of message type HEARTBEAT
function payload_fns.payload_0(buffer, tree, msgid, offset, limit)
    local truncated = false
    if (truncated) then
        tree:add_le(f.HEARTBEAT_custom_mode, 0)
    elseif (offset + 4 <= limit) then
        tree:add_le(f.HEARTBEAT_custom_mode, buffer(offset, 4))
        offset = offset + 4
    elseif (offset < limit) then
        tree:add_le(f.HEARTBEAT_custom_mode, buffer(offset, limit - offset))
        offset = limit
        truncated = true
    else
        tree:add_le(f.HEARTBEAT_custom_mode, 0)
        truncated = true
    end
    if (truncated) then
        tree:add_le(f.HEARTBEAT_type, 0)
    elseif (offset + 1 <= limit) then
        tree:add_le(f.HEARTBEAT_type, buffer(offset, 1))
        offset = offset + 1
    elseif (offset < limit) then
        tree:add_le(f.HEARTBEAT_type, buffer(offset, limit - offset))
        offset = limit
        truncated = true
    else
        tree:add_le(f.HEARTBEAT_type, 0)
        truncated = true
    end
    if (truncated) then
        tree:add_le(f.HEARTBEAT_autopilot, 0)
    elseif (offset + 1 <= limit) then
        tree:add_le(f.HEARTBEAT_autopilot, buffer(offset, 1))
        offset = offset + 1
    elseif (offset < limit) then
        tree:add_le(f.HEARTBEAT_autopilot, buffer(offset, limit - offset))
        offset = limit
        truncated = true
    else
        tree:add_le(f.HEARTBEAT_autopilot, 0)
        truncated = true
    end
    if (truncated) then
        tree:add_le(f.HEARTBEAT_base_mode, 0)
    elseif (offset + 1 <= limit) then
        tree:add_le(f.HEARTBEAT_base_mode, buffer(offset, 1))
        offset = offset + 1
    elseif (offset < limit) then
        tree:add_le(f.HEARTBEAT_base_mode, buffer(offset, limit - offset))
        offset = limit
        truncated = true
    else
        tree:add_le(f.HEARTBEAT_base_mode, 0)
        truncated = true
    end
    if (truncated) then
        tree:add_le(f.HEARTBEAT_system_status, 0)
    elseif (offset + 1 <= limit) then
        tree:add_le(f.HEARTBEAT_system_status, buffer(offset, 1))
        offset = offset + 1
    elseif (offset < limit) then
        tree:add_le(f.HEARTBEAT_system_status, buffer(offset, limit - offset))
        offset = limit
        truncated = true
    else
        tree:add_le(f.HEARTBEAT_system_status, 0)
        truncated = true
    end
    if (truncated) then
        tree:add_le(f.HEARTBEAT_mavlink_version, 0)
    elseif (offset + 1 <= limit) then
        tree:add_le(f.HEARTBEAT_mavlink_version, buffer(offset, 1))
        offset = offset + 1
    elseif (offset < limit) then
        tree:add_le(f.HEARTBEAT_mavlink_version, buffer(offset, limit - offset))
        offset = limit
        truncated = true
    else
        tree:add_le(f.HEARTBEAT_mavlink_version, 0)
        truncated = true
    end
    return offset
end


-- dissector function
function mavlink_proto.dissector(buffer,pinfo,tree)
    local offset = 0
    local msgCount = 0
    
    -- loop through the buffer to extract all the messages in the buffer
    while (offset < buffer:len()) 
    do
        msgCount = msgCount + 1
        local subtree = tree:add (mavlink_proto, buffer(), "MAVLink Protocol ("..buffer:len()..")")

        -- decode protocol version first
        local version = buffer(offset,1):uint()
        local protocolString = ""
    
    	while (true)
		do
            if (version == 0xfe) then
                protocolString = "MAVLink 1.0"
                break
            elseif (version == 0xfd) then
                protocolString = "MAVLink 2.0"
                break
            elseif (version == 0x55) then
                protocolString = "MAVLink 0.9"
                break
            else
                protocolString = "unknown"
                -- some unknown data found, record the begin offset
                if (unknownFrameBeginOffset == 0) then
                    unknownFrameBeginOffset = offset
                end
               
                offset = offset + 1
                
                if (offset < buffer:len()) then
                    version = buffer(offset,1):uint()
                else
                    -- no magic value found in the whole buffer. print the raw data and exit
                    if (unknownFrameBeginOffset ~= 0) then
                        if (msgCount == 1) then
                            pinfo.cols.info:set("Unknown message")
                        else
                            pinfo.cols.info:append("  Unknown message")
                        end
                        size = offset - unknownFrameBeginOffset
                        subtree:add(f.rawpayload, buffer(unknownFrameBeginOffset,size))
                        unknownFrameBeginOffset = 0
                    end
                    return
                end
            end	
        end
        
        if (unknownFrameBeginOffset ~= 0) then
            pinfo.cols.info:append("Unknown message")
            size = offset - unknownFrameBeginOffset
            subtree:add(f.rawpayload, buffer(unknownFrameBeginOffset,size))
            unknownFrameBeginOffset = 0
            -- jump to next loop
            break
        end
        
        -- some Wireshark decoration
        pinfo.cols.protocol = protocolString

        -- HEADER ----------------------------------------
    
        local msgid
        local length
        local incompatibility_flag

        if (version == 0xfe) then
            if (buffer:len() - 2 - offset > 6) then
                -- normal header
                local header = subtree:add("Header")
                header:add(f.magic, buffer(offset,1), version)
                offset = offset + 1
            
                length = buffer(offset,1)
                header:add(f.length, length)
                offset = offset + 1
            
                local sequence = buffer(offset,1)
                header:add(f.sequence, sequence)
                offset = offset + 1
            
                local sysid = buffer(offset,1)
                header:add(f.sysid, sysid)
                offset = offset + 1
        
                local compid = buffer(offset,1)
                header:add(f.compid, compid)
                offset = offset + 1
            
                pinfo.cols.src = "System: "..tostring(sysid:uint())..', Component: '..tostring(compid:uint())
        
                msgid = buffer(offset,1):uint()
                header:add(f.msgid, buffer(offset,1), msgid)
                offset = offset + 1
            else 
                -- handle truncated header
                local hsize = buffer:len() - 2 - offset
                subtree:add(f.rawheader, buffer(offset, hsize))
                offset = offset + hsize
            end
        elseif (version == 0xfd) then
            if (buffer:len() - 2 - offset > 10) then
                -- normal header
                local header = subtree:add("Header")
                header:add(f.magic, buffer(offset,1), version)
                offset = offset + 1
                length = buffer(offset,1)
                header:add(f.length, length)
                offset = offset + 1
                incompatibility_flag = buffer(offset,1):uint()
                header:add(f.incompatibility_flag, buffer(offset,1), incompatibility_flag)
                offset = offset + 1
                local compatibility_flag = buffer(offset,1)
                header:add(f.compatibility_flag, compatibility_flag)
                offset = offset + 1
                local sequence = buffer(offset,1)
                header:add(f.sequence, sequence)
                offset = offset + 1
                local sysid = buffer(offset,1)
                header:add(f.sysid, sysid)
                offset = offset + 1
                local compid = buffer(offset,1)
                header:add(f.compid, compid)
                offset = offset + 1
                pinfo.cols.src = "System: "..tostring(sysid:uint())..', Component: '..tostring(compid:uint())
                msgid = buffer(offset,3):le_uint()
                header:add(f.msgid, buffer(offset,3), msgid)
                offset = offset + 3
            else 
                -- handle truncated header
                local hsize = buffer:len() - 2 - offset
                subtree:add(f.rawheader, buffer(offset, hsize))
                offset = offset + hsize
            end
        end


        -- BODY ----------------------------------------
    
        -- dynamically call the type-specific payload dissector    
        local msgnr = msgid
        local dissect_payload_fn = "payload_"..tostring(msgnr)
        local fn = payload_fns[dissect_payload_fn]
        local limit = buffer:len() - 2

        if (length) then
            length = length:uint()
        else
            length = 0
        end

        if (offset + length < limit) then
            limit = offset + length
        end
    
        if (fn == nil) then
            pinfo.cols.info:append ("Unknown message type   ")
            subtree:add_expert_info(PI_MALFORMED, PI_ERROR, "Unknown message type")
            size = buffer:len() - 2 - offset
            subtree:add(f.rawpayload, buffer(offset,size))
            offset = offset + size
        else
            local payload = subtree:add(f.payload, msgid)
            pinfo.cols.dst:set(messageName[msgid])
            if (msgCount == 1) then
            -- first message should over write the TCP/UDP info
                pinfo.cols.info = messageName[msgid]
            else
                pinfo.cols.info:append("   "..messageName[msgid])
            end
            fn(buffer, payload, msgid, offset, limit)
            offset = limit
        end

        -- CRC ----------------------------------------

        local crc = buffer(offset,2)
        subtree:add_le(f.crc, crc)
        offset = offset + 2

        -- SIGNATURE ----------------------------------

        if (version == 0xfd and incompatibility_flag == 0x01) then
            local signature = subtree:add("Signature")

            local link = buffer(offset,1)
            signature:add(f.signature_link, link)
            offset = offset + 1

            local signature_time = buffer(offset,6):le_uint64()
            local time_secs = signature_time / 100000
            local time_nsecs = (signature_time - (time_secs * 100000)) * 10000
            signature:add(f.signature_time, buffer(offset,6), NSTime.new(signature_time_ref + time_secs:tonumber(), time_nsecs:tonumber()))
            offset = offset + 6

            local signature_signature = buffer(offset,6)
            signature:add(f.signature_signature, signature_signature)
            offset = offset + 6
        end

    end
end


   
-- bind protocol dissector to USER0 linktype

wtap_encap = DissectorTable.get("wtap_encap")
wtap_encap:add(wtap.USER0, mavlink_proto)

-- bind protocol dissector to port 14550 and 14580

local udp_dissector_table = DissectorTable.get("udp.port")
udp_dissector_table:add(14550, mavlink_proto)
udp_dissector_table:add(14580, mavlink_proto)
