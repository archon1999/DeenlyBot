import type { WorshipLabels } from '../../../labels';
import type { QadaRecord } from '../../../../domain';

import { useId, useState } from 'react';
import { varAlpha } from 'minimal-shared/utils';

import { Box, Tab, Card, Tabs } from '@mui/material';

import { Label } from 'src/shared/ui/label';
import { Scrollbar } from 'src/shared/ui/scrollbar';

import { QadaList } from './qada-list';

export function QadaRecordTabs({
  manualQueue,
  history,
  labels,
}: {
  manualQueue: QadaRecord[];
  history: QadaRecord[];
  labels: WorshipLabels;
}) {
  const [tab, setTab] = useState<'queue' | 'history'>('queue');
  const id = useId();
  const panelId = `${id}-panel`;
  return (
    <Card>
      <Tabs
        aria-label={labels.records}
        value={tab}
        onChange={(_, value) => setTab(value)}
        variant="scrollable"
        scrollButtons="auto"
        allowScrollButtonsMobile
        sx={(theme) => ({
          px: { xs: 2, md: 3 },
          py: 1,
          borderBottom: 1,
          borderColor: 'divider',
          '& .MuiTabs-list': { gap: 1 },
          '& .MuiTabs-indicator': { display: 'none' },
          '& .MuiTab-root': {
            px: 1.5,
            minHeight: 44,
            borderRadius: 1.5,
            fontWeight: 500,
            '&.Mui-selected': {
              fontWeight: 500,
              color: 'primary.main',
              bgcolor: varAlpha(theme.vars.palette.primary.mainChannel, 0.08),
            },
          },
          ...theme.applyStyles('dark', {
            '& .MuiTab-root.Mui-selected': {
              color: 'primary.light',
              bgcolor: varAlpha(theme.vars.palette.primary.mainChannel, 0.16),
            },
          }),
        })}
      >
        <Tab
          id={`${id}-queue`}
          aria-controls={panelId}
          label={labels.queue}
          value="queue"
          iconPosition="end"
          icon={<Label color="warning">{manualQueue.length}</Label>}
        />
        <Tab
          id={`${id}-history`}
          aria-controls={panelId}
          label={labels.history}
          value="history"
          iconPosition="end"
          icon={<Label color={tab === 'history' ? 'primary' : 'default'}>{history.length}</Label>}
        />
      </Tabs>
      <Box role="tabpanel" id={panelId} aria-labelledby={`${id}-${tab}`}>
        <Scrollbar
          key={tab}
          autoHide={false}
          fillContent={false}
          ariaLabel={labels[tab]}
          scrollableNodeProps={{ tabIndex: 0 }}
          sx={{
            maxHeight: { xs: 360, md: 480 },
            '& .simplebar-content-wrapper': { overscrollBehavior: 'contain' },
          }}
        >
          <Box sx={{ p: { xs: 2.5, md: 3 } }}>
            <QadaList
              rows={tab === 'queue' ? manualQueue : history}
              history={tab === 'history'}
              labels={labels}
            />
          </Box>
        </Scrollbar>
      </Box>
    </Card>
  );
}
