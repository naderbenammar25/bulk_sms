document.addEventListener('DOMContentLoaded', function() {
    const addToMergeButtons = document.querySelectorAll('.add-to-merge');
    const mergeList = document.getElementById('merge-list');
    const groupsToMergeInput = document.getElementById('groups_to_merge');
    let groupsToMerge = [];

    addToMergeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const groupId = this.getAttribute('data-group-id');
            const groupName = this.parentElement.textContent.trim();
            if (!groupsToMerge.includes(groupId)) {
                groupsToMerge.push(groupId);
                const listItem = document.createElement('div');
                listItem.textContent = groupName;
                listItem.setAttribute('data-group-id', groupId);
                const removeButton = document.createElement('button');
                removeButton.textContent = 'Retirer';
                removeButton.classList.add('remove-from-merge');
                removeButton.addEventListener('click', function() {
                    const index = groupsToMerge.indexOf(groupId);
                    if (index > -1) {
                        groupsToMerge.splice(index, 1);
                        listItem.remove();
                        groupsToMergeInput.value = groupsToMerge.join(',');
                    }
                });
                listItem.appendChild(removeButton);
                mergeList.appendChild(listItem);
                groupsToMergeInput.value = groupsToMerge.join(',');
            }
        });
    });
});