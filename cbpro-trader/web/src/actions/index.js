export const changeActivePeriod = period_name => ({
    type: 'CHANGE_ACTIVE_PERIOD',
    period_name
})

export const changePrimarySection = section_name => ({
    type: 'CHANGE_PRIMARY_SECTION',
    section_name
})

export const changeSecondarySection = section_name => ({
    type: 'CHANGE_SECONDARY_SECTION',
    section_name
})

export const updateBalances = balances => ({
    type: 'UPDATE_BALANCES',
    balances
})

export const updateFlags = flags => ({
    type: 'UPDATE_FLAGS',
    flags
})

export const addPeriod = period_name => ({
    type: 'ADD_PERIOD',
    period_name
})

export const clearPeriods = () => ({
    type: 'CLEAR_PERIODS'
})

export const updateCandlesticks = candlesticks => ({
    type: 'UPDATE_CANDLESTICKS',
    candlesticks
})

export const updateIndicators = indicators => ({
    type: 'UPDATE_INDICATORS',
    indicators
})

export const updateOrders = orders => ({
    type: 'UPDATE_ORDERS',
    orders
})