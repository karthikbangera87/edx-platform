/**
 * The CourseOutlineView is used to render the contents of the course for the Course Outline page.
 * It is a recursive set of views, where each XBlock has its own instance, and each of the children
 * are shown as child CourseOutlineViews.
 *
 * This class extends XBlockOutlineView to add unique capabilities needed by the course outline:
 *  - sections are initially expanded but subsections and other children are shown as collapsed
 *  - changes cause a refresh of the entire section rather than just the view for the changed xblock
 *  - adding units will automatically redirect to the unit page rather than showing them inline
 */
define(["jquery", "underscore", "js/views/xblock_outline", "js/views/utils/view_utils",
        "js/models/xblock_outline_info"],
    function($, _, XBlockOutlineView, ViewUtils, XBlockOutlineInfo) {

        var CourseOutlineView = XBlockOutlineView.extend({
            // takes XBlockOutlineInfo as a model

            templateName: 'course-outline',

            shouldExpandChildren: function() {
                // Expand the children if this xblock's locator is in the initially expanded state
                if (this.initialState && _.indexOf(this.initialState.expanded_locators, this.model.id) >= 0) {
                    return true;
                }
                // Only expand the course and its chapters (aka sections) initially
                var category = this.model.get('category');
                return category === 'course' || category === 'chapter';
            },

            shouldRenderChildren: function() {
                // Render all nodes up to verticals but not below
                return this.model.get('category') !== 'vertical';
            },

            createChildView: function(xblockInfo, parentInfo, parentView) {
                return new CourseOutlineView({
                    model: xblockInfo,
                    parentInfo: parentInfo,
                    initialState: this.initialState,
                    template: this.template,
                    parentView: parentView || this
                });
            },

            getExpandedLocators: function() {
                var expandedLocators = [];
                this.$('.outline-item.is-collapsible').each(function(index, rawElement) {
                    var element = $(rawElement);
                    if (!element.hasClass('collapsed')) {
                        expandedLocators.push(element.data('locator'));
                    }
                });
                return expandedLocators;
            },

            /**
             * Refresh the containing section (if there is one) or else refresh the entire course.
             * Note that the refresh will preserve the expanded state of this view and all of its
             * children.
             * @param viewState The desired initial state of the view, or null if none.
             * @returns {*} A promise representing the refresh operation.
             */
            refresh: function(viewState) {
                var getViewToRefresh, view, expandedLocators;

                getViewToRefresh = function(view) {
                    if (view.model.get('category') === 'chapter' || !view.parentView) {
                        return view;
                    }
                    return getViewToRefresh(view.parentView);
                };

                view = getViewToRefresh(this);
                expandedLocators = view.getExpandedLocators();
                viewState = viewState || {};
                viewState.expanded_locators = expandedLocators.concat(viewState.expanded_locators || []);
                view.initialState = viewState;
                return view.model.fetch({});
            },

            onChildAdded: function(locator, category, event) {
                if (category === 'vertical') {
                    // For units, redirect to the new unit's page in inline edit mode
                    this.onUnitAdded(locator);
                } else if (category === 'chapter' && this.model.hasChildren()) {
                    this.onSectionAdded(locator);
                } else {
                    // For all other block types, refresh the view and do the following:
                    //  - show the new block expanded
                    //  - ensure it is scrolled into view
                    //  - make its name editable
                    this.refresh(this.createNewItemViewState(locator, ViewUtils.getScrollOffset($(event.target))));
                }
            },

            onSectionAdded: function(locator) {
                var self = this,
                    initialState = self.createNewItemViewState(locator),
                    sectionInfo, sectionView;
                // For new chapters in a non-empty view, add a new child view and render it
                // to avoid the expense of refreshing the entire page.
                if (this.model.hasChildren()) {
                    sectionInfo = new XBlockOutlineInfo({
                        id: locator,
                        category: 'chapter'
                    });
                    // Fetch the full xblock info for the section and then create a view for it
                    sectionInfo.fetch().done(function() {
                        sectionView = self.createChildView(sectionInfo, self.model, self);
                        sectionView.initialState = initialState;
                        sectionView.render();
                        self.addChildView(sectionView);
                        sectionView.setViewState(initialState);
                    });
                } else {
                    this.refresh(initialState);
                }
            },

            createNewItemViewState: function(locator, scrollOffset) {
                return {
                    locator_to_show: locator,
                    edit_display_name: true,
                    expanded_locators: [ locator ],
                    scroll_offset: scrollOffset || 0
                };
            }
        });

        return CourseOutlineView;
    }); // end define();