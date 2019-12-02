export const changeActivePeriod = period_name => ({
    type: 'CHANGE_ACTIVE_PERIOD',
    period_name
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