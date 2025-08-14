local mp = require 'mp'

local start_time = nil
local end_time = nil
local previewing = false

local function get_output(command)
    local pipe = io.popen(command)
    local output = pipe:read('*a')
    pipe:close()
    return output 
end

local function last_n_seconds(seconds) 
    local time_pos = mp.get_property_number('time-pos')
    end_time = time_pos
    start_time = math.max(time_pos - seconds, 0)
    clip()
end

local function clip()
    if start_time and end_time then
        mp.osd_message('great job!', 1)
        local command = 'clip "' .. mp.get_property('path') .. '" -ss ' .. start_time .. ' -to ' .. end_time 
        local output = get_output(command)
        mp.osd_message(output, 1)
        mp.set_property_bool('pause', true)
    end
end

local function bleep()
    if start_time and end_time then
        mp.osd_message('great ???!', 1)
        local command = 'bleep "' .. mp.get_property('path') .. '" -ss ' .. start_time .. ' -to ' .. end_time 
        local output = get_output(command)
        mp.osd_message('bleep: ' .. output, 1)
        mp.set_property_bool('pause', true)
    end
end

local function set_start_time()
    start_time = mp.get_property_number('time-pos')
    mp.osd_message('start: ' .. start_time, 1)
end

local function set_end_time()
    end_time = mp.get_property_number('time-pos')
    mp.osd_message('end: '.. end_time, 1)
end

local function last_thirty_seconds()
    last_n_seconds(30)
end

local function last_sixty_seconds()
    last_n_seconds(60)
end

local function warp_to_start_time()
    if start_time then
        mp.set_property_number('time-pos', start_time)
        mp.osd_message(start_time, 1)
    end
end

local function warp_to_end_time()
    if end_time then
        mp.set_property_number('time-pos', end_time)
        mp.osd_message(end_time, 1)
    end
end

local function preview()
    if previewing then
        if end_time then
            local current_time = mp.get_property_number('time-pos')
            if current_time >= end_time then
                mp.set_property_bool('pause', true)
                previewing = false
                mp.osd_message('done', 1)
            end
        end
    end
end

local function toggle_preview()
    if not previewing and start_time and end_time then
        previewing = true 
        mp.set_property_number('time-pos', start_time)
        mp.set_property_bool('pause', false)
        mp.osd_message('>', 1)
    elseif previewing then
        previewing = false 
        mp.osd_message('done', 1)
    else
        mp.osd_message('set start and end', 1)
    end
end

function cycle_audio()
    mp.commandv('cycle', 'audio')
    local aid = mp.get_property_number('aid')

    if aid == nil then
        mp.commandv('cycle', 'audio')
    end
end

mp.register_event('file-loaded', function() 
    -- set audio track (skipping the empty one)
    mp.set_property('aid', 1)
    local aid = mp.get_property_number('aid')

    if aid == nil then
        mp.commandv('cycle', 'audio')
    end
end)

mp.register_event('tick', preview)

mp.add_key_binding('1', 'set-start', set_start_time)
mp.add_key_binding('2', 'set-end', set_end_time)
mp.add_key_binding('w', 'warp-to-start', warp_to_start_time)
mp.add_key_binding('W', 'warp-to-end', warp_to_end_time)
mp.add_key_binding('p', 'toggle-preview', toggle_preview)
mp.add_key_binding('/', 'cycle-audio', cycle_audio)

mp.add_key_binding('f', 'clip', clip)
mp.add_key_binding('r', 'bleep', bleep)

mp.add_key_binding('x', 'last-thirty-seconds', last_thirty_seconds)
