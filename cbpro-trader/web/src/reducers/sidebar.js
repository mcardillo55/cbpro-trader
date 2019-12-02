const sidebar = (state = {indicators: []}, action) => {
    switch (action.type) {
        case 'UPDATE_INDICATORS':
            return {
                ...state,
                indicators: action.indicators
            }
        default:
            return state
    }
}

export default sidebar;