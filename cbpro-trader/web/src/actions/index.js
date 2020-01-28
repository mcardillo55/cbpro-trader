export const changeActivePeriod = period_name => ({
    type: 'CHANGE_ACTIVE_PERIOD',
    period_name
})

export const changeActiveSection = section_name => ({
    type: 'CHANGE_ACTIVE_SECTION',
    section_name
})

export const updateFlags = flags => ({
    type: 'UPDATE_FLAGS',
    flags
})

export const addPeriod = period_name => ({
    type: 'ADD_PERIOD',
    period_name
})

export const updateCandlesticks = candlesticks => ({
    type: 'UPDATE_CANDLESTICKS',
    candlesticks
})

export const updateIndicators = indicators => ({
    type: 'UPDATE_INDICATORS',
    indicators
})