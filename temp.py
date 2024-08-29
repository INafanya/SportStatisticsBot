# Эта функция принимает три аргумента: user_id, state, timeout=300.timeout — это количество секунд, по истечении
# которых состояние будет сброшено, если пользователь не написал новое сообщение. В этом случае тайм-аут
# устанавливается на 5 минут.
#
# Сначала функция извлекает время последнего сообщения пользователя из last_message_time в словаре состояний. Если
# значение равно None, это означает, что это первое сообщение пользователя, поэтому текущее время сохраняется в ключе
# last_message_time.
#
# В противном случае функция вычисляет время с момента последнего сообщения, вычитая last_message_time из текущего
# времени. Если это время больше тайм-аута, функция сбрасывает состояние с помощью state.reset_state() и обновляет
# last_message_time текущим временем.

import asyncio

async def reset_fsm_state(user_id, state, timeout=300):
    last_message_time = state.get('last_message_time')
    if last_message_time is None:
        # First message, save the time
        state['last_message_time'] = asyncio.get_running_loop().time()
        return

    current_time = asyncio.get_running_loop().time()
    time_since_last_message = current_time - last_message_time
    if time_since_last_message > timeout:
        # User has not written a new message within 5 minutes, reset the state
        state.reset_state()
        state['last_message_time'] = current_time