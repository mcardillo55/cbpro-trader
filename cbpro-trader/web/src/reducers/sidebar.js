const sidebar = (state = {indicators: []}, action) => {
    switch (action.type) {
        case 'CHANGE_ACTIVE_SECTION':
            return {
                ...state,
                active_section: action.active_section
            }
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