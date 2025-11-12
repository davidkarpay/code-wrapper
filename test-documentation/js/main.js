// Main JavaScript for Test Documentation Site

// ============================================================================
// NAVIGATION & TOC
// ============================================================================

// Set active nav link based on current page
function initNavigation() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
    }
  });
}

// Generate Table of Contents from headings
function generateTOC() {
  const toc = document.getElementById('toc-list');
  if (!toc) return;

  const headings = document.querySelectorAll('.main-content h2, .main-content h3');
  toc.innerHTML = '';

  headings.forEach((heading, index) => {
    const id = heading.id || `heading-${index}`;
    heading.id = id;

    const li = document.createElement('li');
    li.className = heading.tagName === 'H2' ? 'toc-item' : 'toc-item toc-subitem';

    const a = document.createElement('a');
    a.href = `#${id}`;
    a.className = 'toc-link';
    a.textContent = heading.textContent;
    a.onclick = (e) => {
      e.preventDefault();
      heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
      history.pushState(null, null, `#${id}`);
    };

    li.appendChild(a);
    toc.appendChild(li);
  });
}

// Scroll spy for TOC
function initScrollSpy() {
  const headings = document.querySelectorAll('.main-content h2, .main-content h3');
  const tocLinks = document.querySelectorAll('.toc-link');

  if (headings.length === 0 || tocLinks.length === 0) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          tocLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${id}`) {
              link.classList.add('active');
            }
          });
        }
      });
    },
    { threshold: 0.5, rootMargin: '-100px 0px -80% 0px' }
  );

  headings.forEach(heading => observer.observe(heading));
}

// ============================================================================
// SEARCH FUNCTIONALITY
// ============================================================================

let searchIndex = [];

// Build search index from all content
function buildSearchIndex() {
  const pages = {
    'index.html': 'Dashboard',
    'test-results.html': 'Test Results',
    'recommendations.html': 'Recommendations',
    'test-plan.html': 'Test Plan',
    'summary.html': 'Summary'
  };

  // Index current page
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const pageName = pages[currentPage] || 'Documentation';

  const content = document.querySelector('.main-content');
  if (content) {
    const sections = content.querySelectorAll('h2, h3, p, li');
    sections.forEach((section, index) => {
      if (section.textContent.trim().length > 10) {
        searchIndex.push({
          id: `search-${index}`,
          page: currentPage,
          pageName: pageName,
          title: section.tagName.match(/H[23]/) ? section.textContent : '',
          content: section.textContent,
          element: section
        });
      }
    });
  }
}

// Search modal functionality
function initSearch() {
  const searchTrigger = document.getElementById('search-trigger');
  const searchModal = document.getElementById('search-modal');
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');

  if (!searchTrigger || !searchModal) return;

  // Open search with Cmd/Ctrl + K
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      openSearch();
    }
    if (e.key === 'Escape' && searchModal.classList.contains('active')) {
      closeSearch();
    }
  });

  searchTrigger.addEventListener('click', openSearch);
  searchModal.addEventListener('click', (e) => {
    if (e.target === searchModal) closeSearch();
  });

  function openSearch() {
    searchModal.classList.add('active');
    searchInput.focus();
  }

  function closeSearch() {
    searchModal.classList.remove('active');
    searchInput.value = '';
    searchResults.innerHTML = '';
  }

  // Live search
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();

    if (query.length < 2) {
      searchResults.innerHTML = '<div class="search-result text-muted">Type at least 2 characters to search...</div>';
      return;
    }

    const results = searchIndex.filter(item =>
      item.content.toLowerCase().includes(query) ||
      item.title.toLowerCase().includes(query)
    ).slice(0, 10);

    if (results.length === 0) {
      searchResults.innerHTML = '<div class="search-result text-muted">No results found</div>';
      return;
    }

    searchResults.innerHTML = results.map(result => {
      const context = highlightMatch(result.content, query);
      return `
        <div class="search-result" data-element-id="${result.element.id}">
          <div class="search-result-title">${result.title || result.pageName}</div>
          <div class="search-result-context">${context}</div>
        </div>
      `;
    }).join('');

    // Click handler for results
    searchResults.querySelectorAll('.search-result').forEach((el, index) => {
      el.addEventListener('click', () => {
        const elementId = results[index].element.id;
        if (elementId) {
          results[index].element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          closeSearch();
        }
      });
    });
  });

  function highlightMatch(text, query) {
    const maxLength = 150;
    const lowerText = text.toLowerCase();
    const index = lowerText.indexOf(query.toLowerCase());

    if (index === -1) return text.substring(0, maxLength) + '...';

    const start = Math.max(0, index - 50);
    const end = Math.min(text.length, index + query.length + 50);
    let snippet = text.substring(start, end);

    if (start > 0) snippet = '...' + snippet;
    if (end < text.length) snippet = snippet + '...';

    return snippet.replace(
      new RegExp(query, 'gi'),
      match => `<strong class="text-info">${match}</strong>`
    );
  }
}

// ============================================================================
// COLLAPSIBLE SECTIONS
// ============================================================================

function initCollapsible() {
  document.querySelectorAll('.collapsible-header').forEach(header => {
    header.addEventListener('click', () => {
      const collapsible = header.closest('.collapsible');
      const wasActive = collapsible.classList.contains('active');

      // Close all other collapsibles in the same parent
      const parent = collapsible.parentElement;
      parent.querySelectorAll('.collapsible.active').forEach(active => {
        if (active !== collapsible) {
          active.classList.remove('active');
        }
      });

      // Toggle current
      collapsible.classList.toggle('active', !wasActive);

      // Save state
      const id = collapsible.id;
      if (id) {
        localStorage.setItem(`collapsible-${id}`, !wasActive);
      }
    });
  });

  // Restore state from localStorage
  document.querySelectorAll('.collapsible[id]').forEach(collapsible => {
    const id = collapsible.id;
    const savedState = localStorage.getItem(`collapsible-${id}`);
    if (savedState === 'true') {
      collapsible.classList.add('active');
    }
  });
}

// Expand/collapse all
function expandAll() {
  document.querySelectorAll('.collapsible').forEach(c => c.classList.add('active'));
}

function collapseAll() {
  document.querySelectorAll('.collapsible').forEach(c => c.classList.remove('active'));
}

// ============================================================================
// CHARTS (Chart.js integration)
// ============================================================================

function initCharts() {
  // Test results pie chart
  const testResultsChart = document.getElementById('testResultsChart');
  if (testResultsChart) {
    new Chart(testResultsChart, {
      type: 'doughnut',
      data: {
        labels: ['File READ', 'File WRITE', 'File EDIT', 'Security', 'Path Validation', 'Verification'],
        datasets: [{
          data: [4, 4, 4, 3, 2, 3],
          backgroundColor: [
            '#00d9ff',
            '#00b8d4',
            '#0097a7',
            '#00838f',
            '#006064',
            '#004d56'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#8b949e' }
          },
          title: {
            display: true,
            text: 'Tests by Category',
            color: '#e6edf3'
          }
        }
      }
    });
  }

  // Pass/Fail bar chart
  const passFailChart = document.getElementById('passFailChart');
  if (passFailChart) {
    new Chart(passFailChart, {
      type: 'bar',
      data: {
        labels: ['Passed', 'Failed', 'Skipped'],
        datasets: [{
          label: 'Tests',
          data: [20, 0, 0],
          backgroundColor: ['#3fb950', '#f85149', '#d29922']
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Test Results',
            color: '#e6edf3'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { color: '#8b949e' },
            grid: { color: '#30363d' }
          },
          x: {
            ticks: { color: '#8b949e' },
            grid: { color: '#30363d' }
          }
        }
      }
    });
  }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  generateTOC();
  initScrollSpy();
  buildSearchIndex();
  initSearch();
  initCollapsible();

  // Initialize charts if Chart.js is loaded
  if (typeof Chart !== 'undefined') {
    initCharts();
  }

  // Add smooth scroll to all anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Mobile sidebar toggle (if needed)
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }
});

// Export functions for global access
window.testDocs = {
  expandAll,
  collapseAll,
  initCharts
};
