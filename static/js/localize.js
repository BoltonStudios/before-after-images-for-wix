function localizeStrings( trialDays = 0 ){
console.log("localizeStrings called");
    // Managing the UI strings in one place
    var langs = {
        "en" : {
            "intro": "Easily compare two images with before-and-after image sliders.",
            "add-images-button": "Add Images",
            "free-trial-over": "The free trial is over.",
            "call-to-upgrade": "Upgrade now to keep using Before & After Images.",
            "upgrade-button": "Upgrade App",
            "free-trial-count-down": "Free trial ends in " + trialDays + " days.",
            "nav-link-main": "Main",
            "nav-link-images": "Images",
            "nav-link-layout": "Layout",
            "nav-link-animations": "Animations",
            "nav-link-options": "More",
            "nav-link-support": "Support",
            "nav-link-upgrade": "Upgrade",
            "images-heading": {
                "text": "Images",
                "tooltip": "The shortest image determines the slider height.",
            },
            "before-image-label": "Before",
            "select-image-button": "Upgrade",
            "label-text-label": "Label:",
            "alt-text-label": "Alt Text:",
            "layout-heading": "Layout",
            "orientation-label": "Orientation",
            "offset-label": "Offset",
            "slide-horizontal": {
                "tooltip": "Slide left and right.",
            },
            "slide-vertical": {
                "tooltip": "Slide up and down.",
            },
            "dark-mode-label": "Dark Mode",
            "light-mode-tooltip": {
                "tooltip": "Enable light mode.",
            },
            "dark-mode-tooltip": {
                "tooltip": "Enable dark mode.",
            },
        },
        "es" : {
            "title": "Mi Título",
            "text": "Mi Texto"
        },
        "pt" : {
            "title": "Meu Título",
            "text": "Meu Texto"
        },
        "fr" : {
            "intro": "Comparez facilement deux images avec les curseurs d'image avant et après.",
            "add-images-button": "Ajouter images",
            "free-trial-over": "L'essai gratuit est terminé.",
            "call-to-upgrade": "Mettez à jour maintenant pour continuer à utiliser l'application.",
            "upgrade-button": "Mettre à jour l'application",
            "free-trial-count-down": "L'essai gratuit se termine dans " + trialDays + " jour.",
            "nav-link-main": "Accueil",
            "nav-link-images": "Images",
            "nav-link-layout": "Mise en page",
            "nav-link-animations": "Animations",
            "nav-link-options": "Options",
            "nav-link-support": "Assistance",
            "nav-link-upgrade": "Passer à une version supérieure",
            "images-heading": {
                "text": "Images",
                "tooltip": "L'image la plus courte détermine la hauteur du curseur.",
            },
            "before-image-label": "Avant",
            "after-image-label": "Après",
            "select-image-button": "Sélectionner Image",
            "label-text-label": "Libellé:",
            "alt-text-label": "Texte alternatif:",
            "layout-heading": "Mise en page",
            "orientation-label": "Orientation",
            "offset-label": "Décalage",
            "slide-horizontal": {
                "tooltip": "Glissez vers la gauche et la droite.",
            },
            "slide-vertical": {
                "tooltip": "Glissez vers le haut et vers le bas.",
            },
            "dark-mode-label": "Mode Sombre",
            "light-mode-tooltip": {
                "tooltip": "Activer le mode clair.",
            },
            "dark-mode-tooltip": {
                "tooltip": "Activer le mode sombre.",
            },
        },         
    };
    // Changing the locale in the App Settings    
    var locale = Wix.Utils.getLocale() || 'en';

    // English is the default language
    var localeStrings = langs[locale] || langs['en'];

    // Replacing the the UI elements with the correct text
    for( var id in localeStrings ){

        // Get the translation.
        var translation = typeof localeStrings[ id ] === 'string' ? localeStrings[ id ] : localeStrings[ id ][ "text" ];

        // Check if translation contains tooltip text.
        if( localeStrings[ id ][ "tooltip" ] ){

            // Update tooltip.
            jQuery( '.' + id ).tooltip( 'dispose' )
            .attr( "data-bs-title", localeStrings[ id ][ "tooltip" ] )
            .tooltip( 'enable' );
        }

        if( translation ){

            // Update text
            $( '.' + id ).text( translation );
        }
    }
}