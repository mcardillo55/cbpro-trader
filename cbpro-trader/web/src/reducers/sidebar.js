const sidebar = (state = {indicators: [], flags: {}, orders: [], active_section: "details"}, action) => {
    switch (action.type) {
        case 'CHANGE_ACTIVE_SECTION':
            return {
                ...state,
                active_section: action.section_name
            }
        case 'UPDATE_INDICATORS':
            return {
                ...state,
                indicators: action.indicators
            }
        case 'UPDATE_FLAGS':
            return {
                ...state,
                flags: action.flags
            }
        case 'UPDATE_ORDERS':
            return {
                ...state,
                orders: action.orders
            }
        default:
            return state
    }
}

export default sidebar;