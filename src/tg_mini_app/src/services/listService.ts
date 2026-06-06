import {
  publicApiGetLists,
  publicApiCreateList,
  publicApiUpdateList,
  publicApiDeleteList,
  publicApiSubscribeToList,
  publicApiUnsubscribeFromList,
  publicApiClearList
} from '@/api/sdk.gen';
import type {
  PublicApiGetListsData,
  TagListCreate,
  TagListUpdate,
  TagListResponse,
  TagListsWithSubscriptionResponse
} from '@/api/types.gen';
import { apiData } from '@/services/apiRuntime';

export const listService = {
  getLists(groupId: string, query?: NonNullable<PublicApiGetListsData['query']>): Promise<TagListsWithSubscriptionResponse> {
    return apiData<TagListsWithSubscriptionResponse>(
      publicApiGetLists({ path: { group_id: groupId as any }, query })
    );
  },

  createList(groupId: string, data: TagListCreate): Promise<{ message: TagListResponse, success: boolean }> {
    return apiData<{ message: TagListResponse, success: boolean }>(
      publicApiCreateList({ path: { group_id: groupId as any }, body: data })
    );
  },

  updateList(groupId: string, listId: string, data: TagListUpdate): Promise<{ message: TagListResponse, success: boolean }> {
    return apiData<{ message: TagListResponse, success: boolean }>(
      publicApiUpdateList({ path: { group_id: groupId as any, list_id: listId as any }, body: data })
    );
  },

  deleteList(groupId: string, listId: string): Promise<string> {
    return apiData<string>(
      publicApiDeleteList({ path: { group_id: groupId as any, list_id: listId as any } })
    );
  },

  subscribe(groupId: string, listId: string): Promise<string> {
    return apiData<string>(
      publicApiSubscribeToList({ path: { group_id: groupId as any, list_id: listId as any } })
    );
  },

  unsubscribe(groupId: string, listId: string): Promise<string> {
    return apiData<string>(
      publicApiUnsubscribeFromList({ path: { group_id: groupId as any, list_id: listId as any } })
    );
  },

  clear(groupId: string, listId: string): Promise<string> {
    return apiData<string>(
      publicApiClearList({ path: { group_id: groupId as any, list_id: listId as any } })
    );
  },

};
