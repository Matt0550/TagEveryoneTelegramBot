import {
  publicApiGetLists,
  publicApiCreateList,
  publicApiUpdateList,
  publicApiDeleteList,
  publicApiSubscribeToList,
  publicApiUnsubscribeFromList
} from '@/api/sdk.gen';
import type {
  PublicApiGetListsData,
  TagListCreate,
  TagListUpdate,
  TagListResponse,
  GenericResponseDict
} from '@/api/types.gen';
import { apiData } from '@/services/apiRuntime';

export const listService = {
  getLists(groupId: number, query?: NonNullable<PublicApiGetListsData['query']>): Promise<TagListResponse> {
    return apiData<TagListResponse>(
      publicApiGetLists({ path: { group_id: groupId }, query })
    );
  },

  createList(groupId: number, data: TagListCreate): Promise<{ message: TagListResponse, success: boolean }> {
    return apiData<{ message: TagListResponse, success: boolean }>(
      publicApiCreateList({ path: { group_id: groupId }, body: data })
    );
  },

  updateList(groupId: number, listId: number, data: TagListUpdate): Promise<{ message: TagListResponse, success: boolean }> {
    return apiData<{ message: TagListResponse, success: boolean }>(
      publicApiUpdateList({ path: { group_id: groupId, list_id: listId }, body: data })
    );
  },

  deleteList(groupId: number, listId: number): Promise<GenericResponseDict> {
    return apiData<GenericResponseDict>(
      publicApiDeleteList({ path: { group_id: groupId, list_id: listId } })
    );
  },

  subscribe(groupId: number, listId: number): Promise<GenericResponseDict> {
    return apiData<GenericResponseDict>(
      publicApiSubscribeToList({ path: { group_id: groupId, list_id: listId } })
    );
  },

  unsubscribe(groupId: number, listId: number): Promise<GenericResponseDict> {
    return apiData<GenericResponseDict>(
      publicApiUnsubscribeFromList({ path: { group_id: groupId, list_id: listId } })
    );
  }
};
