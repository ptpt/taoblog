define (require, exports, module) ->
    $   = require '$'
    dom = require './dom'

    truncate = (text, length=255, killwords=false, end='...') ->
        if text.length <= length
            return text
        if killwords
            return text[..length-1] + end
        for index in [length..length/2]
            if text[index] in ['\n', '\t', ' ']
                whitespace = true
            else if whitespace
                return text[..index-1] + end
        return text[..index-1] + end

    flash = (message, category='success') ->
        item = dom ['p', {class: category}, message]
        $('#flash').append item
        $(item).hide();
        $(item).fadeIn('fast').
            delay(if category=='success' then 3000 else 6000).
            fadeOut('slow', ->
                $(this).remove());

    return {
        truncate: truncate
        flash: flash
    }
