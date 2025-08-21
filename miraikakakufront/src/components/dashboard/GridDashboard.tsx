'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useDashboardStore } from '@/store/dashboardStore';
import { useUserModeStore } from '@/store/userModeStore';
import { Widget, WidgetPosition, WidgetSize } from '@/types/dashboard';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Edit, 
  Save, 
  Plus, 
  Settings, 
  Maximize, 
  Minimize,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Move3D,
  Grid3X3,
  RotateCcw
} from 'lucide-react';
import WidgetComponent from './WidgetComponent';
import WidgetSelector from './WidgetSelector';

interface GridDashboardProps {
  className?: string;
}

export default function GridDashboard({ className = '' }: GridDashboardProps) {
  const {
    getActiveLayout,
    isEditMode,
    toggleEditMode,
    selectedWidgetId,
    selectWidget,
    isDragging,
    setDragging,
    moveWidget,
    resizeWidget,
    removeWidget,
    toggleWidgetVisibility,
    lockWidget,
    autoArrangeWidgets,
    gridConfig
  } = useDashboardStore();

  const { config: userConfig, trackFeatureUsage } = useUserModeStore();
  
  const [showWidgetSelector, setShowWidgetSelector] = useState(false);
  const [draggedWidget, setDraggedWidget] = useState<Widget | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const gridRef = useRef<HTMLDivElement>(null);
  
  const activeLayout = getActiveLayout();

  // Calculate grid cell dimensions based on container size
  const [gridDimensions, setGridDimensions] = useState({ cellWidth: 0, cellHeight: 0 });

  const updateGridDimensions = useCallback(() => {
    if (gridRef.current) {
      const container = gridRef.current;
      const containerWidth = container.clientWidth - (gridConfig.containerPadding * 2);
      const containerHeight = container.clientHeight - (gridConfig.containerPadding * 2);
      
      const cellWidth = (containerWidth - (gridConfig.gapSize * (gridConfig.columns - 1))) / gridConfig.columns;
      const cellHeight = (containerHeight - (gridConfig.gapSize * (gridConfig.rows - 1))) / gridConfig.rows;
      
      setGridDimensions({ cellWidth, cellHeight });
    }
  }, [gridConfig]);

  useEffect(() => {
    updateGridDimensions();
    window.addEventListener('resize', updateGridDimensions);
    return () => window.removeEventListener('resize', updateGridDimensions);
  }, [updateGridDimensions]);

  const handleWidgetDragStart = (widget: Widget, event: React.MouseEvent) => {
    if (!isEditMode || widget.isLocked) return;
    
    trackFeatureUsage('widget-drag');
    setDraggedWidget(widget);
    setDragging(true);
    selectWidget(widget.id);
    
    const rect = event.currentTarget.getBoundingClientRect();
    setDragOffset({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    });
  };

  const handleWidgetDrag = useCallback((event: MouseEvent) => {
    if (!draggedWidget || !gridRef.current || !activeLayout) return;

    const gridRect = gridRef.current.getBoundingClientRect();
    const x = event.clientX - gridRect.left - dragOffset.x;
    const y = event.clientY - gridRect.top - dragOffset.y;

    // Convert pixel position to grid position
    const gridX = Math.max(0, Math.min(
      Math.round(x / (gridDimensions.cellWidth + gridConfig.gapSize)),
      gridConfig.columns - draggedWidget.size.width
    ));
    const gridY = Math.max(0, Math.min(
      Math.round(y / (gridDimensions.cellHeight + gridConfig.gapSize)),
      gridConfig.rows - draggedWidget.size.height
    ));

    const newPosition: WidgetPosition = { x: gridX, y: gridY };
    moveWidget(activeLayout.id, draggedWidget.id, newPosition);
  }, [draggedWidget, dragOffset, gridDimensions, gridConfig, activeLayout, moveWidget]);

  const handleWidgetDragEnd = useCallback(() => {
    setDraggedWidget(null);
    setDragging(false);
    setDragOffset({ x: 0, y: 0 });
  }, [setDragging]);

  useEffect(() => {
    if (draggedWidget) {
      window.addEventListener('mousemove', handleWidgetDrag);
      window.addEventListener('mouseup', handleWidgetDragEnd);
      
      return () => {
        window.removeEventListener('mousemove', handleWidgetDrag);
        window.removeEventListener('mouseup', handleWidgetDragEnd);
      };
    }
  }, [draggedWidget, handleWidgetDrag, handleWidgetDragEnd]);

  const handleEditModeToggle = () => {
    toggleEditMode();
    trackFeatureUsage(isEditMode ? 'edit-mode-exit' : 'edit-mode-enter');
  };

  const calculateWidgetStyle = (widget: Widget) => {
    const { cellWidth, cellHeight } = gridDimensions;
    
    return {
      position: 'absolute' as const,
      left: widget.position.x * (cellWidth + gridConfig.gapSize),
      top: widget.position.y * (cellHeight + gridConfig.gapSize),
      width: widget.size.width * cellWidth + (widget.size.width - 1) * gridConfig.gapSize,
      height: widget.size.height * cellHeight + (widget.size.height - 1) * gridConfig.gapSize,
      zIndex: selectedWidgetId === widget.id ? 10 : draggedWidget?.id === widget.id ? 20 : 1,
    };
  };

  if (!activeLayout) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="text-center">
          <div className="text-text-secondary mb-4">
            <Grid3X3 size={64} className="mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-medium text-text-primary mb-2">
              ダッシュボードが見つかりません
            </h3>
            <p className="text-sm">
              新しいダッシュボードを作成してください
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative h-full ${className}`}>
      {/* Dashboard Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-default">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-text-primary">
            {activeLayout.name}
          </h1>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-1 bg-brand-primary/20 text-brand-primary text-xs rounded-md">
              {activeLayout.userMode.toUpperCase()}
            </span>
            {activeLayout.isDefault && (
              <span className="px-2 py-1 bg-status-success/20 text-status-success text-xs rounded-md">
                デフォルト
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {isEditMode && (
            <>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => autoArrangeWidgets(activeLayout.id)}
                className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
                title="自動配置"
              >
                <RotateCcw size={18} />
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setShowWidgetSelector(true);
                  trackFeatureUsage('widget-add');
                }}
                className="p-2 text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-elevated transition-colors"
                title="ウィジェット追加"
              >
                <Plus size={18} />
              </motion.button>
            </>
          )}

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleEditModeToggle}
            className={`p-2 rounded-lg transition-colors ${
              isEditMode
                ? 'bg-status-success text-white'
                : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
            }`}
            title={isEditMode ? '編集完了' : '編集モード'}
          >
            {isEditMode ? <Save size={18} /> : <Edit size={18} />}
          </motion.button>
        </div>
      </div>

      {/* Grid Container */}
      <div 
        ref={gridRef}
        className="relative flex-1 overflow-hidden"
        style={{ 
          padding: gridConfig.containerPadding,
          height: `calc(100% - 73px)` // Subtract header height
        }}
      >
        {/* Grid Background (visible in edit mode) */}
        <AnimatePresence>
          {isEditMode && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage: `
                  linear-gradient(to right, var(--border-subtle) 1px, transparent 1px),
                  linear-gradient(to bottom, var(--border-subtle) 1px, transparent 1px)
                `,
                backgroundSize: `${gridDimensions.cellWidth + gridConfig.gapSize}px ${gridDimensions.cellHeight + gridConfig.gapSize}px`,
                backgroundPosition: '0 0'
              }}
            />
          )}
        </AnimatePresence>

        {/* Widgets */}
        <AnimatePresence>
          {activeLayout.widgets
            .filter(widget => widget.isVisible || isEditMode)
            .map((widget) => (
              <motion.div
                key={widget.id}
                layout={!isDragging}
                style={calculateWidgetStyle(widget)}
                className={`
                  ${!widget.isVisible ? 'opacity-50' : ''}
                  ${isEditMode ? 'cursor-move' : ''}
                  ${selectedWidgetId === widget.id ? 'ring-2 ring-brand-primary' : ''}
                  ${widget.isLocked ? 'border-2 border-status-warning' : ''}
                `}
                onMouseDown={isEditMode ? (e) => handleWidgetDragStart(widget, e) : undefined}
                onClick={() => isEditMode && selectWidget(widget.id)}
              >
                {/* Widget Controls (Edit Mode) */}
                <AnimatePresence>
                  {isEditMode && selectedWidgetId === widget.id && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="absolute -top-10 left-0 flex items-center space-x-1 bg-surface-elevated border border-border-default rounded-lg px-2 py-1 z-30"
                    >
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          lockWidget(activeLayout.id, widget.id, !widget.isLocked);
                        }}
                        className="p-1 text-text-secondary hover:text-text-primary"
                        title={widget.isLocked ? 'ロック解除' : 'ロック'}
                      >
                        {widget.isLocked ? <Unlock size={14} /> : <Lock size={14} />}
                      </button>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleWidgetVisibility(activeLayout.id, widget.id);
                        }}
                        className="p-1 text-text-secondary hover:text-text-primary"
                        title={widget.isVisible ? '非表示' : '表示'}
                      >
                        {widget.isVisible ? <Eye size={14} /> : <EyeOff size={14} />}
                      </button>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeWidget(activeLayout.id, widget.id);
                        }}
                        className="p-1 text-status-danger hover:text-status-danger-hover"
                        title="削除"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c0 1 1 2 2 2v2"/>
                        </svg>
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Widget Component */}
                <WidgetComponent
                  widget={widget}
                  isEditMode={isEditMode}
                  isSelected={selectedWidgetId === widget.id}
                />

                {/* Resize Handle (Edit Mode) */}
                {isEditMode && selectedWidgetId === widget.id && !widget.isLocked && (
                  <div className="absolute bottom-0 right-0 w-4 h-4 bg-brand-primary cursor-se-resize opacity-75 hover:opacity-100">
                    <div className="absolute bottom-0.5 right-0.5 w-2 h-2 border-r-2 border-b-2 border-white" />
                  </div>
                )}
              </motion.div>
            ))}
        </AnimatePresence>

        {/* Empty State */}
        {activeLayout.widgets.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Grid3X3 size={64} className="mx-auto mb-4 text-text-tertiary opacity-50" />
              <h3 className="text-lg font-medium text-text-primary mb-2">
                ウィジェットがありません
              </h3>
              <p className="text-text-secondary text-sm mb-4">
                ウィジェットを追加してダッシュボードをカスタマイズしましょう
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowWidgetSelector(true)}
                className="btn-primary"
              >
                <Plus size={16} className="mr-2" />
                ウィジェット追加
              </motion.button>
            </div>
          </div>
        )}
      </div>

      {/* Widget Selector Modal */}
      <AnimatePresence>
        {showWidgetSelector && (
          <WidgetSelector
            layoutId={activeLayout.id}
            onClose={() => setShowWidgetSelector(false)}
            userMode={userConfig.mode}
          />
        )}
      </AnimatePresence>
    </div>
  );
}