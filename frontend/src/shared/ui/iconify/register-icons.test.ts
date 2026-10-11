import { it, vi, expect, describe, beforeEach } from 'vitest';

const spies = vi.hoisted(() => ({ addCollection: vi.fn(), loadCatalogue: vi.fn() }));
vi.mock('@iconify/react', () => ({ addCollection: spies.addCollection }));
vi.mock('./icon-sets', () => {
  spies.loadCatalogue();
  return { default: { 'solar:pen-bold': { body: '<path d="M0 0" />' } } };
});

beforeEach(() => {
  vi.resetModules();
  vi.clearAllMocks();
});

describe('offline icon loading', () => {
  it('registers navigation icons once without loading the full template catalogue', async () => {
    const icons = await import('./register-icons');
    icons.registerIcons();
    const collections = spies.addCollection.mock.calls.length;
    icons.registerIcons();
    expect(icons.hasRegisteredIcon('custom:menu-duotone')).toBe(true);
    expect(icons.hasRegisteredIcon('solar:file-check-bold-duotone')).toBe(true);
    expect(icons.hasRegisteredIcon('solar:magnifer-linear')).toBe(true);
    expect(icons.hasRegisteredIcon('solar:moon-stars-linear')).toBe(true);
    expect(icons.hasRegisteredIcon('solar:library-linear')).toBe(true);
    expect(icons.hasRegisteredIcon('solar:restart-linear')).toBe(true);
    expect(icons.hasRegisteredIcon('solar:pen-bold')).toBe(false);
    expect(spies.addCollection).toHaveBeenCalledTimes(collections);
    expect(spies.loadCatalogue).not.toHaveBeenCalled();
  });

  it('shares one local catalogue load between simultaneous non-navigation icons', async () => {
    const icons = await import('./register-icons');
    const first = icons.loadIconCatalogue();
    const second = icons.loadIconCatalogue();
    expect(second).toBe(first);
    await first;
    expect(spies.loadCatalogue).toHaveBeenCalledTimes(1);
    expect(icons.hasRegisteredIcon('solar:pen-bold')).toBe(true);
    expect(spies.addCollection).toHaveBeenCalledWith(expect.objectContaining({ prefix: 'solar' }));
  });
});
