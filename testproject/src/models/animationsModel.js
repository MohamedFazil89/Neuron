const animationsData = [
    // ADDED: Sample animation data
    {
        id: '1',
        name: 'Fade In',
        duration: 2,
        properties: {
            translateX: 0,
            translateY: 0,
            opacity: 1
        }
    },
    {
        id: '2',
        name: 'Slide Up',
        duration: 1.5,
        properties: {
            translateX: 0,
            translateY: -100,
            opacity: 1
        }
    }
];

// ADDED: Function to retrieve animation data
exports.getAnimations = async () => {
    return animationsData;
};