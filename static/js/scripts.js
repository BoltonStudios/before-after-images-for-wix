
// Strip the TwentyTwenty HTML and reapply it with new values.
function reinitializeTwentyTwenty( widget ){

    console.log( "reinitializeTwentyTwenty called.");

    // Reset TwentyTwenty elements.
    jQuery("#" + extension_id + "-twentytwenty").unwrap();
    jQuery(".twentytwenty-overlay").remove();
    jQuery(".twentytwenty-handle").remove();
    jQuery(".twentytwenty-before-label").remove();
    jQuery(".twentytwenty-after-label").remove();
    jQuery(".pulser").remove();

    // Reinitialize TwentyTwenty.
    jQuery("#" + extension_id + "-twentytwenty").twentytwenty({
        before_label: widget.beforeLabelText, // Set a custom before label.
        after_label: widget.afterLabelText, // Set a custom after label.
        default_offset_pct: widget.sliderOffsetFloat, // How much of the before image is visible when the page loads.
        orientation: widget.sliderOrientation, // Orientation of the before and after images ('horizontal' or 'vertical')
        no_overlay: widget.noOverlay, //Do not show the overlay with before and after
        move_slider_on_hover: widget.moveOnHover, // Boolean expressed as an int.
        click_to_move: widget.moveOnClickToggle
    });

    // Pulse animation
    if( widget.sliderHandleAnimation == 2 ){
        
        // Remove existing pulser element to handle.
        jQuery( '.twentytwenty-handle' ).prepend( '<span class="pulser"></span>' );
    }
}

// Define the function to ensure the TwentyTwenty container height matches the
// size of the shortest image.
function resizeTwentyTwentyContainer(){

    console.log( "resizeTwentyTwentyContainer called.");

    // Get the height of the shortest image.
    var beforeImage = document.getElementById( extension_id + "-before-image" );
    var afterImage = document.getElementById( extension_id + "-after-image" );
    var shortestImageHeight = beforeImage.offsetHeight < afterImage.offsetHeight ? beforeImage.offsetHeight : afterImage.offsetHeight;

    // Set the height of '.twentytwenty-container' to the height of the shortest image.
    jQuery( '.twentytwenty-container' ).css( "height", shortestImageHeight + "px" );
}

// Update the widget iframe dimensions, as described here:
// https://dev.wix.com/docs/build-apps/developer-tools/extensions/iframes/set-your-app-dimensions
function resizeComponentWindow(){

    console.log( "resizeComponentWindow called.");

    // Initialize variables.
    var beforeImage = document.getElementById( extension_id + "-before-image" );
    var afterImage = document.getElementById( extension_id + "-after-image" );

    // Get the dimensions of the smallest image.
    var imageWidth = beforeImage.offsetWidth < afterImage.offsetWidth ? beforeImage.offsetWidth : afterImage.offsetWidth;
    var imageHeight = beforeImage.offsetHeight < afterImage.offsetHeight ? beforeImage.offsetHeight : afterImage.offsetHeight;

    // Resize the window.
    Wix.resizeComponent(
        {
            width: imageWidth,
            height: imageHeight
        }
    );
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
    var widget = {}

    // Update data attributes.
    slider.dataset.beforeImage = e.beforeImage;
    slider.dataset.beforeLabelText = e.beforeLabelText;
    slider.dataset.beforeAltText = e.beforeAltText;
    slider.dataset.afterImage = e.afterImage;
    slider.dataset.afterLabelText = e.afterLabelText;
    slider.dataset.afterAltText = e.afterAltText;
    slider.dataset.sliderOffset = e.sliderOffset;
    slider.dataset.sliderOffsetFloat = e.sliderOffsetFloat;
    slider.dataset.sliderOrientation = e.sliderOrientation;
    slider.dataset.sliderMouseoverAction = e.sliderMouseoverAction;
    slider.dataset.sliderHandleAnimation = e.sliderHandleAnimation;
    slider.dataset.sliderMoveOnClickToggle = e.sliderMoveOnClickToggle;

    // Update image attributes.
    beforeImage.src = e.beforeImage;
    afterImage.src  = e.afterImage;
    beforeImage.alt = e.beforeAltText;
    afterImage.alt  = e.afterAltText;

    // Update widget object.
    widget.beforeLabelText = slider.dataset.beforeLabelText;
    widget.afterLabelText = slider.dataset.afterLabelText;
    widget.sliderOffsetFloat = slider.dataset.sliderOffsetFloat;
    widget.sliderOrientation = slider.dataset.sliderOrientation;
    widget.noOverlay = false;
    widget.moveOnHover = false;
    widget.moveOnClickToggle = slider.dataset.sliderMoveOnClickToggle;

    // Handle logic for mouseover action.
    switch( slider.dataset.sliderMouseoverAction ){

        // Move slider on hover.
        case 2 :
            widget.noOverlay = false
            widget.moveOnHover = true;
            break;
        // Do nothing on mouseover.
        case 0:
            widget.noOverlay = true;
            widget.moveOnHover = false;
            break;
        // Show overlay on mouseover.
        default :
            break;
    }

    // Restart the TwentyTwenty script.
    // reinitializeTwentyTwenty( widget )
    // Reset TwentyTwenty elements.
    jQuery("#" + extension_id + "-twentytwenty").unwrap();
    jQuery(".twentytwenty-overlay").remove();
    jQuery(".twentytwenty-handle").remove();
    jQuery(".twentytwenty-before-label").remove();
    jQuery(".twentytwenty-after-label").remove();
    jQuery(".pulser").remove();

    // Reinitialize TwentyTwenty.
    jQuery("#" + extension_id + "-twentytwenty").twentytwenty({
        before_label: widget.beforeLabelText, // Set a custom before label.
        after_label: widget.afterLabelText, // Set a custom after label.
        default_offset_pct: widget.sliderOffsetFloat, // How much of the before image is visible when the page loads.
        orientation: widget.sliderOrientation, // Orientation of the before and after images ('horizontal' or 'vertical')
        no_overlay: widget.noOverlay, //Do not show the overlay with before and after
        move_slider_on_hover: widget.moveOnHover, // Boolean expressed as an int.
        click_to_move: widget.moveOnClickToggle
    });

    // Pulse animation
    if( widget.sliderHandleAnimation == 2 ){
        
        // Remove existing pulser element to handle.
        jQuery( '.twentytwenty-handle' ).prepend( '<span class="pulser"></span>' );
    }

    // Update the TwentyTwenty container size.
    // resizeTwentyTwentyContainer();
    // Get the height of the shortest image.
    // var beforeImage = document.getElementById( extension_id + "-before-image" );
    // var afterImage = document.getElementById( extension_id + "-after-image" );
    var shortestImageWidth = beforeImage.offsetWidth < afterImage.offsetWidth ? beforeImage.offsetWidth : afterImage.offsetWidth;
    var shortestImageHeight = beforeImage.offsetHeight < afterImage.offsetHeight ? beforeImage.offsetHeight : afterImage.offsetHeight;

    console.log( "beforeImage.offsetWidth is " + beforeImage.offsetWidth + " and afterImage.offsetWidth is " + afterImage.offsetWidth );
    console.log( "shortestImageWidth is " + shortestImageWidth );

    console.log( "beforeImage.offsetHeight is " + beforeImage.offsetHeight + " and afterImage.offsetHeight is " + afterImage.offsetHeight );
    console.log( "shortestImageHeight is " + shortestImageHeight );

    // Set the height of '.twentytwenty-container' to the height of the shortest image.
    jQuery( '.twentytwenty-container' ).css( "height", shortestImageHeight + "px" );
    jQuery( '.twentytwenty-container' ).css( "opacity", "0.5" );

    // Update the component window size and reset TwentyTwenty.
    // resizeComponentWindow( e )
    // Get the dimensions of the smallest image.
    // var imageWidth = beforeImage.offsetWidth < afterImage.offsetWidth ? beforeImage.offsetWidth : afterImage.offsetWidth;
    // var imageHeight = beforeImage.offsetHeight < afterImage.offsetHeight ? beforeImage.offsetHeight : afterImage.offsetHeight;
    //var shortestImageWidth = beforeImage.offsetWidth < afterImage.offsetWidth ? beforeImage.offsetWidth : afterImage.offsetWidth;

    // Resize the window.
    Wix.resizeComponent(
        {
            width: shortestImageWidth,
            height: shortestImageHeight
        },
        console.log( "resized component to " + shortestImageWidth + "px by " + shortestImageHeight + "px" )
    );

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
            beforeLabelText: slider.dataset.beforeLabelText,
            beforeAltText: slider.dataset.beforeAltText,
            afterImage: slider.dataset.afterImage,
            afterLabelText: slider.dataset.afterLabelText,
            afterAltText: slider.dataset.afterAltText,
            sliderOffset: slider.dataset.sliderOffset,
            sliderOffsetFloat: slider.dataset.sliderOffsetFloat,
            sliderOrientation: slider.dataset.sliderOrientation,
            sliderMouseoverAction: slider.dataset.sliderMouseoverAction,
            sliderHandleAnimation: slider.dataset.sliderHandleAnimation,
            sliderMoveOnClickToggle: slider.dataset.sliderMoveOnClickToggle
        }),
        headers: {
        "Content-type": "application/json; charset=UTF-8"
        }
    });
}