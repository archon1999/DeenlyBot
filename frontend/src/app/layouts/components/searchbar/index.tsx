import type { BoxProps } from '@mui/material/Box';
import type { NavSectionProps } from 'src/shared/ui/nav-section';

import parse from 'autosuggest-highlight/parse';
import match from 'autosuggest-highlight/match';
import { useBoolean } from 'minimal-shared/hooks';
import { useId, useMemo, useState, useEffect, useCallback } from 'react';

import Box from '@mui/material/Box';
import Tooltip from '@mui/material/Tooltip';
import MenuList from '@mui/material/MenuList';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import Dialog, { dialogClasses } from '@mui/material/Dialog';
import MenuItem, { menuItemClasses } from '@mui/material/MenuItem';
import InputBase, { inputBaseClasses } from '@mui/material/InputBase';

import { Label } from 'src/shared/ui/label';
import { useLocale } from 'src/shared/i18n';
import { Scrollbar } from 'src/shared/ui/scrollbar';
import { OutlineIcon } from 'src/shared/ui/outline-icon';

import { ResultItem } from './result-item';
import { applyFilter, flattenNavSections } from './utils';

// ----------------------------------------------------------------------

export type SearchbarProps = BoxProps & {
  data?: NavSectionProps['data'];
};

export function Searchbar({ data: navItems = [], sx, ...other }: SearchbarProps) {
  const theme = useTheme();
  const { language } = useLocale();
  const searchId = useId();
  const labels = {
    uz: { search: 'Qidirish', placeholder: 'Bo‘limlarni qidirish...', empty: 'Natija topilmadi' },
    ru: { search: 'Поиск', placeholder: 'Поиск разделов...', empty: 'Ничего не найдено' },
    en: { search: 'Search', placeholder: 'Search sections...', empty: 'No results found' },
  }[language];

  const { value: open, onFalse: onClose, onTrue: onOpen, onToggle } = useBoolean();
  const [searchQuery, setSearchQuery] = useState('');

  const handleClose = useCallback(() => {
    onClose();
    setSearchQuery('');
  }, [onClose]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        onToggle();
        setSearchQuery('');
      }
    },
    [onToggle]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  const handleSearch = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setSearchQuery(event.target.value);
  }, []);

  const formattedNavItems = flattenNavSections(navItems);

  const dataFiltered = useMemo(
    () =>
      applyFilter({
        inputData: formattedNavItems,
        query: searchQuery,
      }),
    [formattedNavItems, searchQuery]
  );

  const notFound = searchQuery && !dataFiltered.length;

  const renderButton = () => (
    <Box sx={sx} {...other}>
      <Tooltip title={`${labels.search} · Ctrl/⌘ K`}>
        <IconButton
          aria-label={labels.search}
          aria-haspopup="dialog"
          aria-expanded={open}
          aria-controls={open ? searchId : undefined}
          onClick={onOpen}
        >
          <OutlineIcon name="search" width={22} />
        </IconButton>
      </Tooltip>
    </Box>
  );

  const renderResults = () => (
    <MenuList
      disablePadding
      sx={{
        [`& .${menuItemClasses.root}`]: {
          p: 0,
          mb: 0,
          '&:hover': { bgcolor: 'transparent' },
        },
      }}
    >
      {dataFiltered.map((item) => {
        const matchesTitle = match(item.title, searchQuery, { insideWords: true });
        const partsTitle = parse(item.title, matchesTitle);

        const matchesPath = match(item.path, searchQuery, { insideWords: true });
        const partsPath = parse(item.path, matchesPath);

        return (
          <MenuItem disableRipple key={`${item.title}${item.path}`}>
            <ResultItem
              path={partsPath}
              title={partsTitle}
              href={item.path}
              labels={item.group.split('.')}
              onClick={handleClose}
            />
          </MenuItem>
        );
      })}
    </MenuList>
  );

  return (
    <>
      {renderButton()}

      <Dialog
        id={searchId}
        aria-label={labels.search}
        fullWidth
        maxWidth="sm"
        open={open}
        onClose={handleClose}
        transitionDuration={{ enter: theme.transitions.duration.shortest, exit: 100 }}
        sx={[
          {
            [`& .${dialogClasses.paper}`]: { mt: 15, overflow: 'unset' },
            [`& .${dialogClasses.container}`]: { alignItems: 'flex-start' },
          },
        ]}
      >
        <InputBase
          fullWidth
          autoFocus={open}
          placeholder={labels.placeholder}
          value={searchQuery}
          onChange={handleSearch}
          startAdornment={
            <InputAdornment position="start">
              <OutlineIcon name="search" sx={{ color: 'text.disabled' }} />
            </InputAdornment>
          }
          endAdornment={<Label sx={{ letterSpacing: 1, color: 'text.secondary' }}>esc</Label>}
          inputProps={{ id: 'search-input', 'aria-label': labels.placeholder }}
          sx={{
            p: 3,
            borderBottom: `solid 1px ${theme.vars.palette.divider}`,
            [`& .${inputBaseClasses.input}`]: { typography: 'h6' },
          }}
        />

        {notFound ? (
          <Box sx={{ py: 8, px: 3, textAlign: 'center' }}>
            <Typography variant="subtitle1">{labels.empty}</Typography>
            <Typography color="text.secondary">{searchQuery}</Typography>
          </Box>
        ) : (
          <Scrollbar sx={{ p: 2.5, height: 400 }}>{renderResults()}</Scrollbar>
        )}
      </Dialog>
    </>
  );
}
