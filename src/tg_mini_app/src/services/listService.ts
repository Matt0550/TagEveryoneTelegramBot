import {
  publicApiGetLists,
  publicApiCreateList,
  publicApiUpdateList,
  publicApiDeleteList,
  publicApiSubscribeToList,
  publicApiUnsubscribeFromList,
  publicApiClearList,
  publicApiGetListMembers,
  publicApiAddListMember,
  publicApiRemoveListMember,
  publicApiTriggerListMention
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

  getMembers(groupId: string, listId: string): Promise<Array<any>> {
    return apiData<Array<any>>(
      publicApiGetListMembers({ path: { group_id: groupId as any, list_id: listId as any } })
    );
  },

  addMember(groupId: string, listId: string, identifier: string | number): Promise<string> {
    return apiData<string>(
      publicApiAddListMember({ path: { group_id: groupId as any, list_id: listId as any }, body: { identifier } as any })
    );
  },

  removeMember(groupId: string, listId: string, userId: number): Promise<string> {
    return apiData<string>(
      publicApiRemoveListMember({ path: { group_id: groupId as any, list_id: listId as any, user_id: userId as any } })
    );
  },

  triggerMention(groupId: string, listId: string): Promise<string> {
    return apiData<string>(
      publicApiTriggerListMention({ path: { group_id: groupId as any, list_id: listId as any } })
    );
  },

};
