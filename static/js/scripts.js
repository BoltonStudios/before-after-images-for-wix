// Update the widget iframe dimensions, as described here:
// https://dev.wix.com/docs/build-apps/developer-tools/extensions/iframes/set-your-app-dimensions
function resizeComponentWindow(){

    // Source: https://stackoverflow.com/questions/5489946/how-to-wait-for-the-end-of-resize-event-and-only-then-perform-an-action
    clearTimeout( window.resizedFinished );
    window.resizedFinished = setTimeout( function(){

        // Initialize variables.
        var container = jQuery("#" + extension_id + "-twentytwenty");
        var beforeImg = container.find("img:first");
        var beforeWidth = beforeImg.width();
        var beforeHeight = beforeImg.height();

        // Resize the window to the before image dimensions to match TwentyTwenty.
        Wix.resizeComponent({
                width: beforeWidth,
                height: beforeHeight
            },
            // Success
            jQuery( window ).trigger( "resize.twentytwenty" )
            );

    }, 250 );
}

// Do something when the user applies new settings.
function updateWidgetExtension( e ){

    // Print status to the console.
    console.log( "updateWidgetExtension called." );
    console.log( e );

    // Initialize variables.
    var slider = document.getElementById( extension_id + "-twentytwenty" );
    var beforeImage = document.getElementById( extension_id + "-before-image" );
    var afterImage = document.getElementById( extension_id + "-after-image" );
    var noOverlay = false;
    var moveOnHover = false;

    // Update data attributes.
    slider.dataset.beforeImage = e.beforeImage;
    slider.dataset.beforeImageThumbnail = e.beforeImageThumbnail;
    slider.dataset.beforeLabelText = e.beforeLabelText;
    slider.dataset.beforeAltText = e.beforeAltText;
    slider.dataset.afterImage = e.afterImage;
    slider.dataset.afterImageThumbnail = e.afterImageThumbnail;
    slider.dataset.afterLabelText = e.afterLabelText;
    slider.dataset.afterAltText = e.afterAltText;
    slider.dataset.sliderOffset = e.sliderOffset;
    slider.dataset.sliderOffsetFloat = e.sliderOffsetFloat;
    slider.dataset.sliderOrientation = e.sliderOrientation;
    slider.dataset.sliderMouseoverAction = e.sliderMouseoverAction;
    slider.dataset.sliderHandleAnimation = e.sliderHandleAnimation;
    slider.dataset.sliderMoveOnClickToggle = e.sliderMoveOnClickToggle;
    slider.dataset.sliderHandleBorderColor = e.sliderHandleBorderColor;

    // Update image attributes.
    beforeImage.src = e.beforeImage;
    afterImage.src  = e.afterImage;
    beforeImage.alt = e.beforeAltText;
    afterImage.alt  = e.afterAltText;

    // Handle logic for mouseover action.
    switch( e.sliderMouseoverAction ){

        // Move slider on hover.
        case 2 :
            noOverlay = false
            moveOnHover = true;
            break;
        // Do nothing on mouseover.
        case 0:
            noOverlay = true;
            moveOnHover = false;
            break;
        // Show overlay on mouseover.
        default :
            break;
    }

    // Reset TwentyTwenty elements.
    jQuery("#" + extension_id + "-twentytwenty").unwrap();
    jQuery(".twentytwenty-overlay").remove();
    jQuery(".twentytwenty-handle").remove();
    jQuery(".twentytwenty-before-label").remove();
    jQuery(".twentytwenty-after-label").remove();
    jQuery(".pulser").remove();

    // Reinitialize TwentyTwenty.
    jQuery("#" + extension_id + "-twentytwenty").twentytwenty({
        before_label: e.beforeLabelText, // Set a custom before label.
        after_label: e.afterLabelText, // Set a custom after label.
        default_offset_pct: e.sliderOffsetFloat, // How much of the before image is visible when the page loads.
        orientation: e.sliderOrientation, // Orientation of the before and after images ('horizontal' or 'vertical')
        no_overlay: noOverlay, // Do not show the overlay with before and after
        move_slider_on_hover: moveOnHover, // Boolean expressed as an int.
        click_to_move: e.MoveOnClickToggle
    });

    // Pulse animation
    if( e.sliderHandleAnimation == 2 ){
        
        // Remove existing pulser element to handle.
        jQuery( '.twentytwenty-handle' ).prepend( '<span class="pulser"></span>' );
    }

    // Ensure the component window sizes appropriately for the images.
    resizeComponentWindow();

    // Save changes.
    publishWidgetExtension( e )
}

// Do something when the user deletes an extension.
function deleteWidgetExtension( e ){

    // Print status to the console.
    console.log( "deleteWidgetExtension called.");
    console.log( e );

    fetch( url_for_widget, {
        method: "POST",
        body: JSON.stringify({
            extensionId: extension_id,
            action: "delete"
        }),
        headers: {
        "Content-type": "application/json; charset=UTF-8"
        }
    });
}

// Do something when the user saves the website.
function publishWidgetExtension( e ){

    // Print status to the console.
    console.log( "publishWidgetExtension called.");
    console.log( e );

    // Get the extensions current attribute data.
    var slider =  document.getElementById( extension_id + "-twentytwenty" );

    // Send the attribute data to the app in an asynchronous POST request.
    fetch( url_for_widget, {
        method: "POST",
        body: JSON.stringify({
            action: "publish",
            extensionId: slider.dataset.sliderId,
            siteId: Wix.Utils.getSiteOwnerId(),
            userId: Wix.Utils.getUid(),
            instanceId: Wix.Utils.getInstanceId(),
            beforeImage: slider.dataset.beforeImage,
            beforeImageThumbnail: slider.dataset.beforeImageThumbnail,
            beforeLabelText: slider.dataset.beforeLabelText,
            beforeAltText: slider.dataset.beforeAltText,
            afterImage: slider.dataset.afterImage,
            afterImageThumbnail: slider.dataset.afterImageThumbnail,
            afterLabelText: slider.dataset.afterLabelText,
            afterAltText: slider.dataset.afterAltText,
            sliderOffset: slider.dataset.sliderOffset,
            sliderOffsetFloat: slider.dataset.sliderOffsetFloat,
            sliderOrientation: slider.dataset.sliderOrientation,
            sliderMouseoverAction: slider.dataset.sliderMouseoverAction,
            sliderHandleAnimation: slider.dataset.sliderHandleAnimation,
            sliderMoveOnClickToggle: slider.dataset.sliderMoveOnClickToggle,
            sliderHandleBorderColor: slider.dataset.sliderHandleBorderColor
        }),
        headers: {
        "Content-type": "application/json; charset=UTF-8"
        }
    });
}